from unittest.mock import mock_open, patch
from news import filterArticleName, filterDuplicates, generateArticles

def test_filter_duplicate_links():
    articles = [{"title": "Article 1", "link": "link1"},
                {"title": "Article 2", "link": "link2"},
                {"title": "Article 3", "link": "link1"}]
    
    expected = [{"title": "Article 1", "link": "link1"},
                {"title": "Article 2", "link": "link2"}]
    
    result = filterDuplicates(articles)

    assert result == expected
    
@patch("builtins.open", new_callable=mock_open)
def test_filter_articles(mock_file):
    articles = [{"title": "NVDA", "link": "link1"},
                {"title": "Boston", "link": "link2"},
                {"title": "AMD", "link": "link1"}]
    
    with patch("news.json.dump") as mock_json:
        filterArticleName(articles, ["NVDA", "AMD"])
        expected = [{"title": "NVDA", "link": "link1"},
                    {"title": "AMD", "link": "link1"}]
        
        mock_file.assert_called_once_with("filtered_EOD_data.json", "w")
        mock_json.assert_called_once_with(expected, mock_file(), indent=2)

@patch("news.requests.get")
@patch("builtins.open", new_callable=mock_open)
def test_generate_articles(mock_file, mock_get):
    fake_call = [{"title": "this is fake NVDA", "link": "for testing" }]

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = fake_call

    actual = generateArticles("NVDA", "fake_token", 1)
    assert actual == fake_call

    mock_get.assert_called_once_with("https://eodhd.com/api/news?s=NVDA&offset=0&limit=1&api_token=fake_token&fmt=json")
    