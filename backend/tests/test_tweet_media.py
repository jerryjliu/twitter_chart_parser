import pytest

from models import MediaExtractionErrorCode, MediaExtractionSource
from services import tweet_media
from services.tweet_media import TweetMediaError, extract_tweet_images


@pytest.mark.asyncio
async def test_extract_prefers_x_api_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_x_api(tweet_id: str, bearer_token: str, client):  # noqa: ANN001
        assert tweet_id == "123"
        assert bearer_token == "token"
        return ["https://pbs.twimg.com/media/a.jpg"]

    async def fake_syndication(tweet_id: str, client):  # noqa: ANN001
        return ["https://pbs.twimg.com/media/b.jpg"]

    async def fake_fxtwitter(tweet_id: str, client):  # noqa: ANN001
        return ["https://pbs.twimg.com/media/c.jpg"]

    monkeypatch.setattr(tweet_media, "_extract_via_x_api", fake_x_api)
    monkeypatch.setattr(tweet_media, "_extract_via_syndication", fake_syndication)
    monkeypatch.setattr(tweet_media, "_extract_via_fxtwitter_api", fake_fxtwitter)

    result = await extract_tweet_images("https://x.com/user/status/123", x_bearer_token="token")
    assert result.source == MediaExtractionSource.x_api
    assert result.image_urls == ["https://pbs.twimg.com/media/a.jpg"]


@pytest.mark.asyncio
async def test_extract_falls_back_when_x_api_auth_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_x_api(tweet_id: str, bearer_token: str, client):  # noqa: ANN001
        raise TweetMediaError(
            code=MediaExtractionErrorCode.auth_required,
            message="bad token",
            status_code=401,
        )

    async def fake_syndication(tweet_id: str, client):  # noqa: ANN001
        return ["https://pbs.twimg.com/media/fallback.jpg"]

    async def fake_fxtwitter(tweet_id: str, client):  # noqa: ANN001
        return ["https://pbs.twimg.com/media/from-fx.jpg"]

    monkeypatch.setattr(tweet_media, "_extract_via_x_api", fake_x_api)
    monkeypatch.setattr(tweet_media, "_extract_via_syndication", fake_syndication)
    monkeypatch.setattr(tweet_media, "_extract_via_fxtwitter_api", fake_fxtwitter)

    result = await extract_tweet_images("https://x.com/user/status/123", x_bearer_token="token")
    assert result.source == MediaExtractionSource.syndication
    assert result.image_urls == ["https://pbs.twimg.com/media/fallback.jpg"]
    assert result.warnings


@pytest.mark.asyncio
async def test_extract_raises_no_media_found(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_syndication(tweet_id: str, client):  # noqa: ANN001
        return []

    async def fake_fxtwitter(tweet_id: str, client):  # noqa: ANN001
        return []

    async def fake_html(tweet_url: str, client):  # noqa: ANN001
        return []

    monkeypatch.setattr(tweet_media, "_extract_via_syndication", fake_syndication)
    monkeypatch.setattr(tweet_media, "_extract_via_fxtwitter_api", fake_fxtwitter)
    monkeypatch.setattr(tweet_media, "_extract_via_html_meta", fake_html)

    with pytest.raises(TweetMediaError) as exc_info:
        await extract_tweet_images("https://x.com/user/status/123")

    assert exc_info.value.code == MediaExtractionErrorCode.no_media_found


@pytest.mark.asyncio
async def test_extract_rejects_invalid_url() -> None:
    with pytest.raises(TweetMediaError) as exc_info:
        await extract_tweet_images("not-a-url")

    assert exc_info.value.code == MediaExtractionErrorCode.invalid_tweet_url


@pytest.mark.asyncio
async def test_extract_falls_back_to_fxtwitter(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_syndication(tweet_id: str, client):  # noqa: ANN001
        return []

    async def fake_fxtwitter(tweet_id: str, client):  # noqa: ANN001
        return ["https://pbs.twimg.com/media/from-fxtwitter.jpg?name=orig"]

    monkeypatch.setattr(tweet_media, "_extract_via_syndication", fake_syndication)
    monkeypatch.setattr(tweet_media, "_extract_via_fxtwitter_api", fake_fxtwitter)

    result = await extract_tweet_images("https://x.com/user/status/123")
    assert result.source == MediaExtractionSource.fxtwitter_api
    assert result.image_urls == ["https://pbs.twimg.com/media/from-fxtwitter.jpg?name=orig"]
