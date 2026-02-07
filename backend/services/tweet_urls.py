"""Tweet URL parsing and normalization utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse


_TWEET_PATH_RE = re.compile(r"^/(?P<username>[A-Za-z0-9_]+)/status/(?P<tweet_id>\d+)(?:/.*)?$")


@dataclass(frozen=True)
class TweetUrlInfo:
    """Parsed tweet URL components."""

    username: str
    tweet_id: str
    normalized_url: str


class InvalidTweetUrlError(ValueError):
    """Raised when a URL is not a valid tweet status URL."""



def parse_tweet_url(tweet_url: str) -> TweetUrlInfo:
    """Parse and normalize a tweet URL from x.com/twitter.com domains."""
    if not tweet_url or not tweet_url.strip():
        raise InvalidTweetUrlError("Tweet URL is required")

    cleaned = tweet_url.strip()
    parsed = urlparse(cleaned)

    if parsed.scheme not in {"http", "https"}:
        raise InvalidTweetUrlError("Tweet URL must start with http:// or https://")

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if host not in {"x.com", "twitter.com"}:
        raise InvalidTweetUrlError("Tweet URL must be from x.com or twitter.com")

    match = _TWEET_PATH_RE.match(parsed.path)
    if not match:
        raise InvalidTweetUrlError("Tweet URL must match /<user>/status/<tweet_id>")

    username = match.group("username")
    tweet_id = match.group("tweet_id")
    normalized_url = f"https://x.com/{username}/status/{tweet_id}"
    return TweetUrlInfo(username=username, tweet_id=tweet_id, normalized_url=normalized_url)



def normalize_tweet_url(tweet_url: str) -> str:
    """Return canonical x.com URL for a tweet."""
    return parse_tweet_url(tweet_url).normalized_url



def extract_tweet_id(tweet_url: str) -> str:
    """Extract numeric tweet ID from URL."""
    return parse_tweet_url(tweet_url).tweet_id
