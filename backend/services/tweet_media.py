"""Tweet media extraction service with multi-strategy fallbacks."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any

import httpx

from models import MediaExtractionErrorCode, MediaExtractionSource
from services.tweet_urls import InvalidTweetUrlError, parse_tweet_url


class TweetMediaError(Exception):
    """Domain error for tweet media extraction failures."""

    def __init__(
        self,
        code: MediaExtractionErrorCode,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


@dataclass(frozen=True)
class ExtractedTweetMedia:
    """Normalized media extraction output."""

    tweet_id: str
    normalized_tweet_url: str
    image_urls: list[str]
    source: MediaExtractionSource
    warnings: list[str]


async def extract_tweet_images(
    tweet_url: str,
    x_bearer_token: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> ExtractedTweetMedia:
    """Extract ordered photo URLs from a tweet URL."""
    try:
        parsed = parse_tweet_url(tweet_url)
    except InvalidTweetUrlError as exc:
        raise TweetMediaError(
            code=MediaExtractionErrorCode.invalid_tweet_url,
            message=str(exc),
            status_code=422,
        ) from exc

    should_close = client is None
    http_client = client or httpx.AsyncClient(timeout=20.0)
    warnings: list[str] = []

    try:
        if x_bearer_token:
            try:
                x_api_urls = await _extract_via_x_api(parsed.tweet_id, x_bearer_token, http_client)
                if x_api_urls:
                    return ExtractedTweetMedia(
                        tweet_id=parsed.tweet_id,
                        normalized_tweet_url=parsed.normalized_url,
                        image_urls=x_api_urls,
                        source=MediaExtractionSource.x_api,
                        warnings=warnings,
                    )
                warnings.append("X API returned no photo media; attempting fallback extractors.")
            except TweetMediaError as exc:
                if exc.code in {
                    MediaExtractionErrorCode.auth_required,
                    MediaExtractionErrorCode.upstream_error,
                }:
                    warnings.append(f"X API path unavailable ({exc.code.value}); attempting fallback extractors.")
                else:
                    raise

        syndication_urls = await _extract_via_syndication(parsed.tweet_id, http_client)
        if syndication_urls:
            return ExtractedTweetMedia(
                tweet_id=parsed.tweet_id,
                normalized_tweet_url=parsed.normalized_url,
                image_urls=syndication_urls,
                source=MediaExtractionSource.syndication,
                warnings=warnings,
            )

        fxtwitter_urls = await _extract_via_fxtwitter_api(parsed.tweet_id, http_client)
        if fxtwitter_urls:
            warnings.append("Using fxtwitter API fallback for media extraction.")
            return ExtractedTweetMedia(
                tweet_id=parsed.tweet_id,
                normalized_tweet_url=parsed.normalized_url,
                image_urls=fxtwitter_urls,
                source=MediaExtractionSource.fxtwitter_api,
                warnings=warnings,
            )

        html_urls = await _extract_via_html_meta(parsed.normalized_url, http_client)
        if html_urls:
            warnings.append("Using HTML metadata fallback, which may return partial media set.")
            return ExtractedTweetMedia(
                tweet_id=parsed.tweet_id,
                normalized_tweet_url=parsed.normalized_url,
                image_urls=html_urls,
                source=MediaExtractionSource.html_meta,
                warnings=warnings,
            )

        raise TweetMediaError(
            code=MediaExtractionErrorCode.no_media_found,
            message="No image media found for this tweet URL.",
            status_code=404,
            details={"tweet_id": parsed.tweet_id},
        )
    finally:
        if should_close:
            await http_client.aclose()


async def _request_with_retries(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    max_attempts: int = 3,
    retryable_statuses: set[int] | None = None,
    **kwargs: Any,
) -> httpx.Response:
    """Make resilient HTTP requests for transient upstream failures."""
    retryable_statuses = retryable_statuses or {429, 500, 502, 503, 504}

    delay = 0.3
    for attempt in range(1, max_attempts + 1):
        try:
            response = await client.request(method, url, **kwargs)
            if response.status_code not in retryable_statuses or attempt == max_attempts:
                return response
        except httpx.RequestError:
            if attempt == max_attempts:
                raise
        await asyncio.sleep(delay)
        delay *= 2

    raise RuntimeError("unreachable")


async def _extract_via_x_api(
    tweet_id: str,
    bearer_token: str,
    client: httpx.AsyncClient,
) -> list[str]:
    """Extract tweet photo URLs via official X API lookup."""
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "expansions": "attachments.media_keys",
        "media.fields": "type,url,preview_image_url",
        "tweet.fields": "attachments",
    }

    response = await _request_with_retries(
        client,
        "GET",
        f"https://api.x.com/2/tweets/{tweet_id}",
        headers=headers,
        params=params,
    )

    if response.status_code in {401, 403}:
        raise TweetMediaError(
            code=MediaExtractionErrorCode.auth_required,
            message="X API authentication failed for provided bearer token.",
            status_code=response.status_code,
        )

    if response.status_code == 404:
        raise TweetMediaError(
            code=MediaExtractionErrorCode.unsupported_tweet,
            message="Tweet not found via X API.",
            status_code=404,
        )

    if response.status_code >= 400:
        raise TweetMediaError(
            code=MediaExtractionErrorCode.upstream_error,
            message=f"X API lookup failed with status {response.status_code}.",
            status_code=502,
        )

    payload = response.json()
    media_items = payload.get("includes", {}).get("media", [])
    urls: list[str] = []
    for media in media_items:
        if media.get("type") != "photo":
            continue
        candidate = media.get("url") or media.get("preview_image_url")
        if candidate:
            urls.append(candidate)

    return _dedupe_urls(urls)


async def _extract_via_syndication(tweet_id: str, client: httpx.AsyncClient) -> list[str]:
    """Best-effort extraction from syndication endpoint."""
    response = await _request_with_retries(
        client,
        "GET",
        "https://cdn.syndication.twimg.com/tweet-result",
        params={"id": tweet_id},
        headers={"User-Agent": "Mozilla/5.0"},
    )

    if response.status_code >= 400:
        return []

    payload = response.json()
    urls: list[str] = []

    for media in payload.get("mediaDetails", []):
        media_type = media.get("type")
        if media_type != "photo":
            continue
        candidate = media.get("media_url_https") or media.get("media_url") or media.get("url")
        if candidate:
            urls.append(candidate)

    for media in payload.get("photos", []):
        if isinstance(media, dict):
            candidate = media.get("url") or media.get("src")
            if candidate:
                urls.append(candidate)

    entities = payload.get("entities", {})
    for media in entities.get("media", []):
        if media.get("type") != "photo":
            continue
        candidate = media.get("media_url_https") or media.get("media_url")
        if candidate:
            urls.append(candidate)

    return _dedupe_urls(urls)


async def _extract_via_html_meta(tweet_url: str, client: httpx.AsyncClient) -> list[str]:
    """Best-effort extraction from tweet HTML metadata."""
    response = await _request_with_retries(
        client,
        "GET",
        tweet_url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    if response.status_code >= 400:
        return []

    text = response.text
    # Keep strict to pbs media images, avoids random page assets.
    matches = re.findall(r"https://pbs\.twimg\.com/media/[A-Za-z0-9_\-]+(?:\?[^\"'\s<>]+)?", text)
    return _dedupe_urls(matches)


async def _extract_via_fxtwitter_api(tweet_id: str, client: httpx.AsyncClient) -> list[str]:
    """Best-effort extraction from fxtwitter public API JSON."""
    response = await _request_with_retries(
        client,
        "GET",
        f"https://api.fxtwitter.com/status/{tweet_id}",
        headers={"User-Agent": "Mozilla/5.0"},
    )

    if response.status_code >= 400:
        return []

    try:
        payload = response.json()
    except ValueError:
        return []

    tweet = payload.get("tweet", {})
    media = tweet.get("media", {})
    urls: list[str] = []

    for item in media.get("photos", []):
        if not isinstance(item, dict):
            continue
        candidate = item.get("url")
        if candidate:
            urls.append(candidate)

    if not urls:
        for item in media.get("all", []):
            if not isinstance(item, dict):
                continue
            if item.get("type") != "photo":
                continue
            candidate = item.get("url")
            if candidate:
                urls.append(candidate)

    return _dedupe_urls(urls)



def _dedupe_urls(urls: list[str]) -> list[str]:
    """Preserve order while removing duplicates and empty strings."""
    seen: set[str] = set()
    deduped: list[str] = []
    for url in urls:
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped
