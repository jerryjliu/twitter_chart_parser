from fastapi.testclient import TestClient

from main import app
from models import MediaExtractionSource
from services.tweet_media import ExtractedTweetMedia


def test_parse_tweet_end_to_end_with_mocks(monkeypatch) -> None:  # noqa: ANN001
    from api import parse as parse_api

    async def fake_extract(tweet_url: str, x_bearer_token=None):  # noqa: ANN001
        return ExtractedTweetMedia(
            tweet_id="111",
            normalized_tweet_url="https://x.com/demo/status/111",
            image_urls=[
                "https://pbs.twimg.com/media/one.jpg",
                "https://pbs.twimg.com/media/two.jpg",
            ],
            source=MediaExtractionSource.syndication,
            warnings=["fallback extractor used"],
        )

    async def fake_parse(image_url: str, api_key: str, settings):  # noqa: ANN001
        from models import ParsedImageResult, TableResult

        if image_url.endswith("two.jpg"):
            return ParsedImageResult(
                image_url=image_url,
                filename="two.jpg",
                success=True,
                markdown="second image",
                tables=[
                    TableResult(
                        page_number=1,
                        row_count=2,
                        column_count=2,
                        markdown="| A | B |\n| --- | --- |\n| 1 | 2 |",
                    )
                ],
            )

        return ParsedImageResult(
            image_url=image_url,
            filename="one.jpg",
            success=True,
            markdown="first image",
            tables=[],
        )

    monkeypatch.setattr(parse_api, "extract_tweet_images", fake_extract)
    monkeypatch.setattr(parse_api, "parse_image_from_url", fake_parse)

    client = TestClient(app)
    response = client.post(
        "/parse-tweet",
        json={
            "api_key": "llx-valid",
            "tweet_url": "https://x.com/demo/status/111",
            "tier": "agentic",
            "enable_chart_parsing": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tweet_id"] == "111"
    assert payload["source"] == "syndication"
    assert len(payload["results"]) == 2
    assert "## Image 1" in payload["combined_markdown"]
    assert payload["warnings"]
