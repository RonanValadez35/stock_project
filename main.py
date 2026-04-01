import os
import news
import summarizer
import email_sender
from dotenv import load_dotenv
import requests
import json

def main():

    # Use news.py class functions
    load_dotenv()
    ticker = "NVDA"
    num_articles = 100
    token = os.getenv("API_KEY_EODHD")

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

    filter_name = news.filterArticleName(articles, ticker)

    #write filtered data to file
    with open("filtered_EOD_data.json", "w") as f:
        json.dump(filter_name,f, indent=2)

    print("filtered_EOD_data.json created")

###############################################################

    # Use summarizer.py class functions
    with open('filtered_EOD_data.json') as json_file:
        articles = json.load(json_file)


    prompt = summarizer.buildRequestPrompt(articles)
    response = summarizer.getResponse(prompt)

    summarizer.formatDoc(response.message.content)
    print("Finished formatting document preparing to send")

###############################################################

    # Use email_sender.py functions
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("RECIPIENT_EMAIL")

    email_sender.sendEmail(sender, password, receiver, "response.txt")

    print("Finished Running")

if __name__ == "__main__":
    main()


