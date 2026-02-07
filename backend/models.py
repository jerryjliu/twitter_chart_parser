"""Shared API and domain models for the twitter chart parser backend."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class ParseTier(str, Enum):
    """Supported LlamaParse tiers."""

    fast = "fast"
    cost_effective = "cost_effective"
    agentic = "agentic"
    agentic_plus = "agentic_plus"


class MediaExtractionSource(str, Enum):
    """Origin of extracted tweet media URLs."""

    x_api = "x_api"
    syndication = "syndication"
    fxtwitter_api = "fxtwitter_api"
    html_meta = "html_meta"


class MediaExtractionErrorCode(str, Enum):
    """High-level media extraction failure categories."""

    invalid_tweet_url = "INVALID_TWEET_URL"
    auth_required = "AUTH_REQUIRED"
    no_media_found = "NO_MEDIA_FOUND"
    unsupported_tweet = "UNSUPPORTED_TWEET"
    upstream_error = "UPSTREAM_ERROR"


class ValidateLlamaKeyRequest(BaseModel):
    """Request payload for LlamaCloud API key validation."""

    api_key: str = Field(min_length=1)


class ValidateLlamaKeyResponse(BaseModel):
    """Response payload for LlamaCloud API key validation."""

    valid: bool
    message: str


class ExtractTweetImagesRequest(BaseModel):
    """Request payload for image extraction from a tweet URL."""

    tweet_url: str = Field(min_length=1)
    x_bearer_token: str | None = None


class ExtractTweetImagesResponse(BaseModel):
    """Response payload containing extracted image URLs."""

    tweet_id: str
    normalized_tweet_url: str
    image_urls: list[HttpUrl]
    source: MediaExtractionSource
    warnings: list[str] = Field(default_factory=list)


class TableResult(BaseModel):
    """Table extracted from parsed image page items."""

    page_number: int
    row_count: int
    column_count: int
    markdown: str
    bbox: list[float] | None = None


class ParsedImageResult(BaseModel):
    """Per-image parsing output."""

    image_url: HttpUrl
    filename: str
    success: bool
    markdown: str = ""
    tables: list[TableResult] = Field(default_factory=list)
    error: str | None = None


class ParseTweetRequest(BaseModel):
    """Request payload for full tweet parse orchestration."""

    api_key: str = Field(min_length=1)
    tweet_url: str = Field(min_length=1)
    tier: ParseTier = ParseTier.agentic
    enable_chart_parsing: bool = True
    x_bearer_token: str | None = None


class ParseTweetResponse(BaseModel):
    """Response payload for tweet parse orchestration."""

    tweet_id: str
    normalized_tweet_url: str
    source: MediaExtractionSource
    results: list[ParsedImageResult]
    combined_markdown: str
    warnings: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Uniform API error payload."""

    error_code: str
    message: str
    details: dict[str, Any] | None = None
