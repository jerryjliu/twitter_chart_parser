from services.tweet_urls import InvalidTweetUrlError, extract_tweet_id, normalize_tweet_url, parse_tweet_url


def test_parse_x_url_success() -> None:
    parsed = parse_tweet_url("https://x.com/llama_index/status/1234567890")
    assert parsed.username == "llama_index"
    assert parsed.tweet_id == "1234567890"
    assert parsed.normalized_url == "https://x.com/llama_index/status/1234567890"


def test_parse_twitter_url_normalizes_to_x() -> None:
    url = "https://twitter.com/someuser/status/987654321?s=20"
    assert normalize_tweet_url(url) == "https://x.com/someuser/status/987654321"
    assert extract_tweet_id(url) == "987654321"


def test_parse_rejects_non_status_paths() -> None:
    try:
        parse_tweet_url("https://x.com/home")
        assert False, "expected InvalidTweetUrlError"
    except InvalidTweetUrlError as exc:
        assert "status" in str(exc)


def test_parse_rejects_non_twitter_domains() -> None:
    try:
        parse_tweet_url("https://example.com/user/status/123")
        assert False, "expected InvalidTweetUrlError"
    except InvalidTweetUrlError as exc:
        assert "x.com or twitter.com" in str(exc)
