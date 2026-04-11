import json
import requests


def filterArticleName(articles: list[dict], names: list[str]) -> None:
    filtered_articles = []
    for article in articles:
        if any(name in article["title"] for name in names):
            filtered_articles.append(article)
    
    #write filtered data to file
    with open("filtered_EOD_data.json", "w") as f:
        json.dump(filtered_articles,f, indent=2)
    

def filterDuplicates(articles: list[dict]) ->  list[dict]:
    unique_articles = []
    seen = set()
    for article in articles:
        if article["link"] not in seen:
            seen.add(article["link"])
            unique_articles.append(article)
    return unique_articles

def generateArticles(ticker: str, token: str, num_articles: int) -> list[dict]:
    url = f'https://eodhd.com/api/news?s={ticker}&offset=0&limit={num_articles}&api_token={token}&fmt=json'

    # call EOD API
    response = requests.get(url)

    if response.status_code == 200:
        with open("EOD_data.json", "w") as f:
            json.dump(response.json(),f, indent=2)
        return response.json()

    else:
        print("Error with API call")
        raise Exception(f"""API call for {ticker} failed with 
                        status code {response.status_code}""")