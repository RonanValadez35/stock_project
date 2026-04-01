import os
from dotenv import load_dotenv 
import json
import requests

# load_dotenv()
# ticker = "NVDA"
# token = os.getenv("API_KEY_EODHD")
# num_articles = 100
# url = f'https://eodhd.com/api/news?s={ticker}&offset=0&limit={num_articles}&api_token={token}&fmt=json'
# data = {}
#filter articles based on name to reduce input
def filterArticleName(articles: list[dict], ticker: str) -> list[dict]:
    filtered_articles = []
    for input in articles:
        if ticker in input["title"]:
            filtered_articles.append(input)
    return filtered_articles


# response = requests.get(url)

# if response.status_code == 200:
#     data = response.json()

#     with open("EOD_data.json", "w") as f:
#         json.dump(data,f, indent=2)
# else:
#     print("Error with API call")



# # load data from file
# with open('EOD_data.json') as json_file:
#     articles = json.load(json_file)

# filter_name = filterArticleName(articles)

# #write filtered data to file
# with open("filtered_EOD_data.json", "w") as f:
#     json.dump(filter_name,f, indent=2)

# # # print("The URL is: " + filter_name[0]["url"])

# # print(buildRequestPrompt(filter_name))



