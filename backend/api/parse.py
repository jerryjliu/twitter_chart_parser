"""Tweet parsing orchestration routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models import ErrorResponse, ParseTweetRequest, ParseTweetResponse
from services.llamacloud_parser import ParseSettings, build_combined_markdown, parse_image_from_url
from services.tweet_media import TweetMediaError, extract_tweet_images

router = APIRouter(tags=["parse"])


@router.post(
    "/parse-tweet",
    response_model=ParseTweetResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def parse_tweet(request: ParseTweetRequest) -> ParseTweetResponse:
    """Extract tweet images and parse each with LlamaCloud."""
    if not request.api_key.startswith("llx-"):
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_API_KEY",
                "message": "LlamaCloud API key must start with llx-",
            },
        )

    try:
        extracted = await extract_tweet_images(
            tweet_url=request.tweet_url,
            x_bearer_token=request.x_bearer_token,
        )
    except TweetMediaError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "error_code": exc.code.value,
                "message": exc.message,
                "details": exc.details,
            },
        ) from exc

    settings = ParseSettings(
        tier=request.tier,
        enable_chart_parsing=request.enable_chart_parsing,
    )

    results = []
    for image_url in extracted.image_urls:
        parsed = await parse_image_from_url(
            image_url=image_url,
            api_key=request.api_key,
            settings=settings,
        )
        results.append(parsed)

    combined_markdown = build_combined_markdown(results)
    warnings = list(extracted.warnings)
    failed = [result.filename for result in results if not result.success]
    if failed:
        warnings.append(f"Failed to parse {len(failed)} image(s): {', '.join(failed)}")

    return ParseTweetResponse(
        tweet_id=extracted.tweet_id,
        normalized_tweet_url=extracted.normalized_tweet_url,
        source=extracted.source,
        results=results,
        combined_markdown=combined_markdown,
        warnings=warnings,
    )
