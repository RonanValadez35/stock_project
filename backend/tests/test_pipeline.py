from unittest.mock import patch

from backend import pipeline


@patch("backend.pipeline.summarizer.formatDoc", return_value="formatted summary\n")
@patch(
    "backend.pipeline.summarizer.getResponse",
    return_value={"message": {"content": "raw summary"}},
)
@patch("backend.pipeline.summarizer.buildRequestPrompt", return_value="prompt")
@patch("backend.pipeline.news.filterArticleName")
@patch("backend.pipeline.news.filterDuplicates")
@patch("backend.pipeline.news.generateArticles")
def test_run_summary_passes_data_in_memory(
    mock_generate,
    mock_duplicates,
    mock_filter,
    mock_prompt,
    mock_response,
    mock_format,
):
    fetched = [{"title": "NVDA one", "link": "one"}]
    unique = [{"title": "NVDA one", "link": "one"}]
    filtered = [{"title": "NVDA one", "link": "one"}]
    mock_generate.return_value = fetched
    mock_duplicates.return_value = unique
    mock_filter.return_value = filtered

    actual = pipeline.run_summary(
        ["NVDA"],
        ["NVDA", "Nvidia"],
        "token",
        num_articles=10,
    )

    assert actual == "formatted summary\n"
    mock_generate.assert_called_once_with("NVDA", "token", 10)
    mock_duplicates.assert_called_once_with(fetched)
    mock_filter.assert_called_once_with(unique, ["NVDA", "Nvidia"])
    mock_prompt.assert_called_once_with(filtered, ["NVDA"])
    mock_response.assert_called_once_with("prompt")
    mock_format.assert_called_once_with("raw summary", max_length=80)


@patch("backend.pipeline.email_sender.sendEmail")
@patch("backend.pipeline.run_summary", return_value="summary")
@patch("backend.pipeline.load_dotenv")
def test_generate_summary_runs_pipeline_and_sends_email(
    mock_load_dotenv,
    mock_run_summary,
    mock_send_email,
    monkeypatch,
):
    monkeypatch.setenv("API_KEY_EODHD", "api-token")
    monkeypatch.setenv("EMAIL_USER", "sender@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "password")
    monkeypatch.setenv("RECIPIENT_EMAIL", "default@example.com")

    actual = pipeline.generate_summary(
        tickers=["NVDA"],
        recipient_email="requested@example.com",
        num_articles=25,
        stock_names=["NVDA", "Nvidia"],
    )

    assert actual == "summary"
    mock_load_dotenv.assert_called_once_with(pipeline.ENV_FILE)
    mock_run_summary.assert_called_once_with(
        tickers=["NVDA"],
        stock_names=["NVDA", "Nvidia"],
        token="api-token",
        num_articles=25,
    )
    mock_send_email.assert_called_once_with(
        "sender@example.com",
        "password",
        "requested@example.com",
        "summary",
    )
