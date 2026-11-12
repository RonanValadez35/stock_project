from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.api import app, limiter


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("backend.api.generate_summary")
def test_create_summary_validates_and_starts_background_job(mock_generate):
    response = client.post(
        "/api/summaries",
        json={
            "tickers": [" nvda ", "AMD", "nvda"],
            "email": "analyst@example.com",
            "num_articles": 25,
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "message": "Summary generation started",
        "tickers": ["NVDA", "AMD"],
    }
    mock_generate.assert_called_once_with(
        tickers=["NVDA", "AMD"],
        recipient_email="analyst@example.com",
        num_articles=25,
        stock_names=None,
    )


def test_create_summary_rejects_invalid_input():
    response = client.post(
        "/api/summaries",
        json={"tickers": ["bad ticker"], "num_articles": 151},
    )

    assert response.status_code == 422


def test_cors_preflight_allows_configured_frontend():
    response = client.options(
        "/api/summaries",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
