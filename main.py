import os
import news
import summarizer
import email_sender
from dotenv import load_dotenv
import json

def main():

    # Use news.py class functions
    load_dotenv()
    tickers = ["NVDA", "AMD"]
    stock_names = ["NVDA", "AMD", "Nvidia", "Advanced Micro Devices"]
    num_articles = 150
    token = os.getenv("API_KEY_EODHD")
    articles = []
    for ticker in tickers:
        article = news.generateArticles(ticker, token, num_articles)
        articles.extend(article)

    unique_articles = news.filterDuplicates(articles)
    news.filterArticleName(unique_articles, stock_names)

    print("filtered_EOD_data.json created")

###############################################################

    # Use summarizer.py class functions
    with open('filtered_EOD_data.json') as json_file:
        articles = json.load(json_file)


    prompt = summarizer.buildRequestPrompt(articles, tickers)
    response = summarizer.getResponse(prompt)
    summarizer.formatDoc(response['message']['content'])
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