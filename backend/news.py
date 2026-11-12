import requests


def filterArticleName(articles: list[dict], names: list[str]) -> list[dict]:
    """Return articles whose title contains at least one requested name."""
    return [
        article
        for article in articles
        if any(name in article["title"] for name in names)
    ]


def filterDuplicates(articles: list[dict]) -> list[dict]:
    unique_articles = []
    seen = set()
    for article in articles:
        if article["link"] not in seen:
            seen.add(article["link"])
            unique_articles.append(article)
    return unique_articles


def generateArticles(ticker: str, token: str, num_articles: int) -> list[dict]:
    url = (
        "https://eodhd.com/api/news"
        f"?s={ticker}&offset=0&limit={num_articles}&api_token={token}&fmt=json"
    )

    # call EOD API
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    raise RuntimeError(
        f"API call for {ticker} failed with status code {response.status_code}"
    )
