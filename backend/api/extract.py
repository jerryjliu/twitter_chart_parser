"""Tweet image extraction routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models import ErrorResponse, ExtractTweetImagesRequest, ExtractTweetImagesResponse
from services.tweet_media import TweetMediaError, extract_tweet_images

router = APIRouter(tags=["extract"])


@router.post(
    "/extract-tweet-images",
    response_model=ExtractTweetImagesResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def extract_images(request: ExtractTweetImagesRequest) -> ExtractTweetImagesResponse:
    """Extract image attachments from a tweet URL."""
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

    return ExtractTweetImagesResponse(
        tweet_id=extracted.tweet_id,
        normalized_tweet_url=extracted.normalized_tweet_url,
        image_urls=extracted.image_urls,
        source=extracted.source,
        warnings=extracted.warnings,
    )
