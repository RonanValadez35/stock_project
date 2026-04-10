import json
import requests


def filterArticleName(articles: list[dict], ticker: str) -> None:
    filtered_articles = []
    for input in articles:
        if ticker in input["title"]:
            filtered_articles.append(input)
    
    #write filtered data to file
    with open("filtered_EOD_data.json", "w") as f:
        json.dump(filtered_articles,f, indent=2)
    


def generateArticles(ticker: str, token: str, num_articles: int) -> list[dict]:
    url = f'https://eodhd.com/api/news?s={ticker}&offset=0&limit={num_articles}&api_token={token}&fmt=json'
    data = {}

    # call EOD API
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        with open("EOD_data.json", "w") as f:
            json.dump(data,f, indent=2)
    else:
        print("Error with API call")

    # load data from file
    with open('EOD_data.json') as json_file:
        articles = json.load(json_file)

    return articles