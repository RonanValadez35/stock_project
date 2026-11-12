"""FastAPI application for creating stock-summary jobs."""

import logging
import os
import re

from fastapi import BackgroundTasks, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from pipeline import ENV_FILE, generate_summary


load_dotenv(ENV_FILE)
logger = logging.getLogger(__name__)
TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.-]{0,9}$")
SUMMARY_RATE_LIMIT = os.getenv("SUMMARY_RATE_LIMIT", "5/minute")


def _cors_origins() -> list[str]:
    configured = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Stock Summary API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class SummaryRequest(BaseModel):
    """Validated input for a summary job."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    tickers: list[str] = Field(min_length=1, max_length=10)
    recipient_email: str | None = Field(default=None, max_length=254)
    num_articles: int = Field(default=150, ge=1, le=150)
    stock_names: list[str] | None = Field(default=None, min_length=1, max_length=30)

    @model_validator(mode="before")
    @classmethod
    def accept_email_alias(cls, value: object) -> object:
        if isinstance(value, dict) and "email" in value:
            if "recipient_email" in value:
                raise ValueError("provide either email or recipient_email, not both")
            value = {**value, "recipient_email": value["email"]}
            value.pop("email")
        return value

    @field_validator("tickers", mode="before")
    @classmethod
    def validate_tickers(cls, value: object) -> list[str]:
        if not isinstance(value, list):
            raise ValueError("tickers must be a list")
        if not 1 <= len(value) <= 10:
            raise ValueError("tickers must contain between 1 and 10 items")

        normalized: list[str] = []
        for ticker in value:
            if not isinstance(ticker, str):
                raise ValueError("every ticker must be a string")
            candidate = ticker.strip().upper()
            if not TICKER_PATTERN.fullmatch(candidate):
                raise ValueError(f"invalid ticker: {ticker}")
            if candidate not in normalized:
                normalized.append(candidate)
        return normalized

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("recipient_email must be a valid email address")
        return value

    @field_validator("stock_names")
    @classmethod
    def validate_stock_names(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if any(not name.strip() for name in value):
            raise ValueError("stock_names cannot contain blank values")
        return value


class SummaryAccepted(BaseModel):
    status: str
    message: str
    tickers: list[str]


def _generate_summary_job(summary_request: SummaryRequest) -> None:
    try:
        generate_summary(
            tickers=summary_request.tickers,
            recipient_email=summary_request.recipient_email,
            num_articles=summary_request.num_articles,
            stock_names=summary_request.stock_names,
        )
    except Exception:
        logger.exception(
            "Summary job failed for tickers %s",
            summary_request.tickers,
        )


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post(
    "/api/summaries",
    response_model=SummaryAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
@limiter.limit(SUMMARY_RATE_LIMIT)
async def create_summary(
    request: Request,
    summary_request: SummaryRequest,
    background_tasks: BackgroundTasks,
) -> SummaryAccepted:
    background_tasks.add_task(_generate_summary_job, summary_request)
    return SummaryAccepted(
        status="accepted",
        message="Summary generation started",
        tickers=summary_request.tickers,
    )
