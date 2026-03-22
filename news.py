import finnhub
import os
from dotenv import load_dotenv 
import json
import requests

load_dotenv()
ticker = "NVDA"

finnhub_client  = finnhub.Client(api_key=os.getenv("API_KEY"))

#filter articles based on name to reduce input
def filterArticleName(articles: list[dict]) -> list[dict]:
    filtered_articles = []
    for input in articles:
        if ticker in input["headline"]:
            filtered_articles.append(input)
    return filtered_articles


articles = finnhub_client.company_news(ticker, _from="2026-03-18", to="2026-03-18")

with open("data.json", "w") as f:
    json.dump(articles,f, indent=2)


filter_name = filterArticleName(articles)

with open("filtered_data.json", "w") as f:
    json.dump(filter_name,f, indent=2)

# print("The URL is: " + filter_name[0]["url"])

print(buildRequestPrompt(filter_name))



