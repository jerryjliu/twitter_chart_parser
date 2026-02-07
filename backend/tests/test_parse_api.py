from fastapi.testclient import TestClient

from main import app
from models import MediaExtractionSource
from services.tweet_media import ExtractedTweetMedia


def test_parse_tweet_rejects_invalid_api_key() -> None:
    client = TestClient(app)
    response = client.post(
        "/parse-tweet",
        json={
            "api_key": "bad",
            "tweet_url": "https://x.com/user/status/123",
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error_code"] == "INVALID_API_KEY"


def test_parse_tweet_success(monkeypatch) -> None:  # noqa: ANN001
    from api import parse as parse_api

    async def fake_extract(tweet_url: str, x_bearer_token=None):  # noqa: ANN001
        return ExtractedTweetMedia(
            tweet_id="123",
            normalized_tweet_url="https://x.com/user/status/123",
            image_urls=["https://pbs.twimg.com/media/a.jpg"],
            source=MediaExtractionSource.syndication,
            warnings=[],
        )

    async def fake_parse_image_from_url(image_url: str, api_key: str, settings):  # noqa: ANN001
        from models import ParsedImageResult

        return ParsedImageResult(
            image_url=image_url,
            filename="a.jpg",
            success=True,
            markdown="hello",
            tables=[],
        )

    monkeypatch.setattr(parse_api, "extract_tweet_images", fake_extract)
    monkeypatch.setattr(parse_api, "parse_image_from_url", fake_parse_image_from_url)

    client = TestClient(app)
    response = client.post(
        "/parse-tweet",
        json={
            "api_key": "llx-123",
            "tweet_url": "https://x.com/user/status/123",
            "tier": "agentic",
            "enable_chart_parsing": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tweet_id"] == "123"
    assert payload["results"][0]["success"] is True


def test_parse_tweet_partial_failure(monkeypatch) -> None:  # noqa: ANN001
    from api import parse as parse_api

    async def fake_extract(tweet_url: str, x_bearer_token=None):  # noqa: ANN001
        return ExtractedTweetMedia(
            tweet_id="123",
            normalized_tweet_url="https://x.com/user/status/123",
            image_urls=[
                "https://pbs.twimg.com/media/a.jpg",
                "https://pbs.twimg.com/media/b.jpg",
            ],
            source=MediaExtractionSource.syndication,
            warnings=[],
        )

    async def fake_parse_image_from_url(image_url: str, api_key: str, settings):  # noqa: ANN001
        from models import ParsedImageResult

        if image_url.endswith("b.jpg"):
            return ParsedImageResult(image_url=image_url, filename="b.jpg", success=False, error="parse failed")
        return ParsedImageResult(image_url=image_url, filename="a.jpg", success=True, markdown="ok", tables=[])

    monkeypatch.setattr(parse_api, "extract_tweet_images", fake_extract)
    monkeypatch.setattr(parse_api, "parse_image_from_url", fake_parse_image_from_url)

    client = TestClient(app)
    response = client.post(
        "/parse-tweet",
        json={
            "api_key": "llx-123",
            "tweet_url": "https://x.com/user/status/123",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["results"]) == 2
    assert any("Failed to parse" in warning for warning in payload["warnings"])
