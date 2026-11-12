from unittest.mock import patch

from backend.news import filterArticleName, filterDuplicates, generateArticles


def test_filter_duplicate_links():
    articles = [{"title": "Article 1", "link": "link1"},
                {"title": "Article 2", "link": "link2"},
                {"title": "Article 3", "link": "link1"}]
    expected = [{"title": "Article 1", "link": "link1"},
                {"title": "Article 2", "link": "link2"}]

    result = filterDuplicates(articles)

    assert result == expected


def test_filter_articles():
    articles = [{"title": "NVDA", "link": "link1"},
                {"title": "Boston", "link": "link2"},
                {"title": "AMD", "link": "link1"}]
    actual = filterArticleName(articles, ["NVDA", "AMD"])
    expected = [{"title": "NVDA", "link": "link1"},
                {"title": "AMD", "link": "link1"}]

    assert actual == expected


@patch("backend.news.requests.get")
def test_generate_articles(mock_get):
    fake_call = [{"title": "this is fake NVDA", "link": "for testing" }]

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = fake_call

    actual = generateArticles("NVDA", "fake_token", 1)
    assert actual == fake_call

    mock_get.assert_called_once_with(
        "https://eodhd.com/api/news"
        "?s=NVDA&offset=0&limit=1&api_token=fake_token&fmt=json"
    )
