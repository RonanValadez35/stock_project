"""In-memory orchestration for fetching and summarizing stock news."""

import os
from pathlib import Path

from dotenv import load_dotenv

import email_sender
import news
import summarizer


ENV_FILE = Path(__file__).with_name(".env")


def _response_content(response: object) -> str:
    """Extract message content from Ollama's mapping-like response."""
    try:
        message = response["message"]  # type: ignore[index]
        return message["content"]  # type: ignore[index]
    except (KeyError, TypeError):
        message = getattr(response, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content
        raise ValueError("Summarizer response did not contain message content")


def run_summary(
    tickers: list[str],
    stock_names: list[str],
    token: str,
    num_articles: int = 150,
    max_line_length: int = 80,
) -> str:
    """Fetch, filter, summarize, and format stock news entirely in memory."""
    articles: list[dict] = []
    for ticker in tickers:
        articles.extend(news.generateArticles(ticker, token, num_articles))

    unique_articles = news.filterDuplicates(articles)
    filtered_articles = news.filterArticleName(unique_articles, stock_names)
    prompt = summarizer.buildRequestPrompt(filtered_articles, tickers)
    response = summarizer.getResponse(prompt)
    return summarizer.formatDoc(
        _response_content(response),
        max_length=max_line_length,
    )


def generate_summary(
    tickers: list[str],
    recipient_email: str | None = None,
    num_articles: int = 150,
    stock_names: list[str] | None = None,
) -> str:
    """Generate a stock summary and send it to the requested recipient."""
    load_dotenv(ENV_FILE)
    token = os.getenv("API_KEY_EODHD")
    if not token:
        raise ValueError("API_KEY_EODHD is not configured")

    summary = run_summary(
        tickers=tickers,
        stock_names=stock_names or tickers,
        token=token,
        num_articles=num_articles,
    )

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = recipient_email or os.getenv("RECIPIENT_EMAIL")
    email_sender.sendEmail(sender, password, receiver, summary)
    return summary
