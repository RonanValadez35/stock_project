"use client";

import { FormEvent, KeyboardEvent, useRef, useState } from "react";

const MAX_TICKERS = 5;
const TICKER_PATTERN = /^[A-Z][A-Z0-9.-]{0,9}$/;
const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

type FormErrors = {
  email?: string;
  tickers?: string;
  form?: string;
};

type ValidationIssue = {
  loc?: Array<string | number>;
  msg?: string;
};

function getServerErrors(payload: unknown): FormErrors {
  if (!payload || typeof payload !== "object") {
    return { form: "Something went wrong. Please try again." };
  }

  const response = payload as {
    detail?: string | ValidationIssue[];
    message?: string;
  };

  if (Array.isArray(response.detail)) {
    const errors: FormErrors = {};

    for (const issue of response.detail) {
      const field = issue.loc?.at(-1);
      const message = issue.msg ?? "This value is invalid.";

      if (field === "email" || field === "recipient_email") {
        errors.email = message;
      } else if (field === "tickers") {
        errors.tickers = message;
      } else if (!errors.form) {
        errors.form = message;
      }
    }

    return Object.keys(errors).length > 0
      ? errors
      : { form: "The server could not validate your request." };
  }

  return {
    form:
      (typeof response.detail === "string" && response.detail) ||
      response.message ||
      "Something went wrong. Please try again.",
  };
}

export default function Home() {
  const [email, setEmail] = useState("");
  const [tickerInput, setTickerInput] = useState("");
  const [tickers, setTickers] = useState<string[]>([]);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function addTicker(rawTicker: string): boolean {
    const ticker = rawTicker.trim().toUpperCase();

    if (!ticker) {
      setTickerInput("");
      return true;
    }

    if (!TICKER_PATTERN.test(ticker)) {
      setErrors((current) => ({
        ...current,
        tickers:
          "Use 1–10 letters, numbers, periods, or hyphens, starting with a letter.",
      }));
      return false;
    }

    if (tickers.includes(ticker)) {
      setErrors((current) => ({
        ...current,
        tickers: `${ticker} has already been added.`,
      }));
      setTickerInput("");
      return false;
    }

    if (tickers.length >= MAX_TICKERS) {
      setErrors((current) => ({
        ...current,
        tickers: `You can add up to ${MAX_TICKERS} tickers.`,
      }));
      return false;
    }

    setTickers((current) => [...current, ticker]);
    setTickerInput("");
    setErrors((current) => ({ ...current, tickers: undefined, form: undefined }));
    setIsSuccess(false);
    return true;
  }

  function handleTickerChange(value: string) {
    if (!value.includes(",")) {
      setTickerInput(value.toUpperCase());
      setErrors((current) => ({ ...current, tickers: undefined, form: undefined }));
      return;
    }

    const parts = value.split(",");
    const completed = parts.slice(0, -1);
    const remainder = parts.at(-1) ?? "";
    const nextTickers = [...tickers];

    for (const rawTicker of completed) {
      const ticker = rawTicker.trim().toUpperCase();

      if (!ticker) {
        continue;
      }

      if (!TICKER_PATTERN.test(ticker)) {
        setTickerInput(ticker);
        setErrors((current) => ({
          ...current,
          tickers:
            "Use 1–10 letters, numbers, periods, or hyphens, starting with a letter.",
        }));
        return;
      }

      if (nextTickers.includes(ticker)) {
        setTickerInput("");
        setErrors((current) => ({
          ...current,
          tickers: `${ticker} has already been added.`,
        }));
        return;
      }

      if (nextTickers.length >= MAX_TICKERS) {
        setTickerInput(ticker);
        setErrors((current) => ({
          ...current,
          tickers: `You can add up to ${MAX_TICKERS} tickers.`,
        }));
        return;
      }

      nextTickers.push(ticker);
    }

    setTickers(nextTickers);
    setTickerInput(remainder.toUpperCase());
    setErrors((current) => ({ ...current, tickers: undefined, form: undefined }));
    setIsSuccess(false);
  }

  function handleTickerKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if ((event.key === "Enter" || event.key === ",") && tickerInput.trim()) {
      event.preventDefault();
      addTicker(tickerInput);
      return;
    }

    if (event.key === "Backspace" && !tickerInput && tickers.length > 0) {
      setTickers((current) => current.slice(0, -1));
      setErrors((current) => ({ ...current, tickers: undefined, form: undefined }));
      setIsSuccess(false);
    }
  }

  function removeTicker(ticker: string) {
    setTickers((current) => current.filter((item) => item !== ticker));
    setErrors((current) => ({ ...current, tickers: undefined, form: undefined }));
    setIsSuccess(false);
    inputRef.current?.focus();
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSuccess(false);

    const normalizedEmail = email.trim();
    let submittedTickers = tickers;
    const nextErrors: FormErrors = {};
    const emailInput = event.currentTarget.elements.namedItem("email");

    if (!normalizedEmail) {
      nextErrors.email = "Enter the email where you want the summary sent.";
    } else if (emailInput instanceof HTMLInputElement && !emailInput.checkValidity()) {
      nextErrors.email = "Enter a valid email address.";
    }

    if (tickerInput.trim()) {
      const pendingTicker = tickerInput.trim().toUpperCase();

      if (!TICKER_PATTERN.test(pendingTicker)) {
        nextErrors.tickers =
          "Use 1–10 letters, numbers, periods, or hyphens, starting with a letter.";
      } else if (!submittedTickers.includes(pendingTicker)) {
        if (submittedTickers.length >= MAX_TICKERS) {
          nextErrors.tickers = `You can add up to ${MAX_TICKERS} tickers.`;
        } else {
          submittedTickers = [...submittedTickers, pendingTicker];
          setTickers(submittedTickers);
          setTickerInput("");
        }
      } else {
        setTickerInput("");
      }
    }

    if (submittedTickers.length === 0) {
      nextErrors.tickers = "Add at least one ticker.";
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setErrors({});
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/summaries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: normalizedEmail,
          tickers: submittedTickers,
        }),
      });

      const payload: unknown = await response.json().catch(() => null);

      if (!response.ok) {
        setErrors(getServerErrors(payload));
        return;
      }

      setIsSuccess(true);
      setErrors({});
    } catch {
      setErrors({
        form:
          "We couldn’t reach the server. Check your connection and try again.",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#071a17] px-5 py-8 text-[#14201d] sm:px-8 sm:py-12">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-24 top-24 h-72 w-72 rounded-full bg-[#32d583]/10 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-24 bottom-12 h-80 w-80 rounded-full bg-[#f4c95d]/10 blur-3xl"
      />

      <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-6xl items-center">
        <section className="grid w-full overflow-hidden rounded-[2rem] border border-white/10 bg-[#f4f1e8] shadow-[0_32px_100px_rgba(0,0,0,0.35)] lg:grid-cols-[0.95fr_1.05fr]">
          <div className="relative flex min-h-[20rem] flex-col justify-between overflow-hidden bg-[#0d2c26] p-8 text-[#f7f4eb] sm:p-12 lg:min-h-[42rem] lg:p-14">
            <div
              aria-hidden="true"
              className="absolute -right-16 top-24 h-52 w-52 rounded-full border border-[#45dd95]/20"
            />
            <div
              aria-hidden="true"
              className="absolute -right-2 top-40 h-52 w-52 rounded-full border border-[#45dd95]/10"
            />

            <div className="relative">
              <div className="mb-12 flex items-center gap-3 text-sm font-semibold tracking-[0.18em] text-[#a8e8c5] uppercase">
                <span className="grid h-9 w-9 place-items-center rounded-full border border-[#45dd95]/30 bg-[#45dd95]/10">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    className="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <path d="M4 16l4.5-5 3.5 3 6-7" />
                    <path d="M15 7h3v3" />
                  </svg>
                </span>
                Market Brief
              </div>

              <p className="mb-4 text-sm font-medium text-[#7dcfa2]">
                Your watchlist, distilled.
              </p>
              <h1 className="max-w-md text-4xl leading-[1.05] font-semibold tracking-[-0.04em] sm:text-5xl lg:text-[3.6rem]">
                The signal, without the noise.
              </h1>
              <p className="mt-6 max-w-md text-base leading-7 text-[#b9cbc5] sm:text-lg">
                Choose the companies you follow and get a clear, concise stock
                news summary delivered straight to your inbox.
              </p>
            </div>

            <div className="relative mt-10 flex items-center gap-3 border-t border-white/10 pt-6 text-sm text-[#91aaa2]">
              <span className="h-2 w-2 rounded-full bg-[#45dd95] shadow-[0_0_0_5px_rgba(69,221,149,0.1)]" />
              Fresh market context, prepared on demand
            </div>
          </div>

          <div className="flex items-center p-7 sm:p-12 lg:p-16">
            <div className="w-full">
              <div className="mb-9">
                <p className="mb-2 text-xs font-bold tracking-[0.18em] text-[#218458] uppercase">
                  Build your brief
                </p>
                <h2 className="text-3xl font-semibold tracking-[-0.035em] text-[#10231e] sm:text-4xl">
                  What are you watching?
                </h2>
                <p className="mt-3 text-sm leading-6 text-[#66736e] sm:text-base">
                  Add up to five ticker symbols. We’ll send the summary when it’s
                  ready.
                </p>
              </div>

              <form onSubmit={handleSubmit} noValidate className="space-y-6">
                <div>
                  <label
                    htmlFor="email"
                    className="mb-2 block text-sm font-semibold text-[#243832]"
                  >
                    Email address
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);
                      setErrors((current) => ({
                        ...current,
                        email: undefined,
                        form: undefined,
                      }));
                      setIsSuccess(false);
                    }}
                    aria-invalid={Boolean(errors.email)}
                    aria-describedby={errors.email ? "email-error" : undefined}
                    placeholder="you@example.com"
                    className="h-13 w-full rounded-xl border border-[#cbd1cb] bg-white/70 px-4 text-base text-[#17231f] outline-none transition placeholder:text-[#98a19d] focus:border-[#278a60] focus:ring-4 focus:ring-[#278a60]/10 aria-[invalid=true]:border-[#c74848] aria-[invalid=true]:ring-4 aria-[invalid=true]:ring-[#c74848]/10"
                  />
                  {errors.email && (
                    <p id="email-error" className="mt-2 text-sm text-[#a83232]">
                      {errors.email}
                    </p>
                  )}
                </div>

                <div>
                  <div className="mb-2 flex items-center justify-between gap-4">
                    <label
                      htmlFor="ticker-input"
                      className="block text-sm font-semibold text-[#243832]"
                    >
                      Ticker symbols
                    </label>
                    <span className="text-xs font-medium text-[#7a8580]">
                      {tickers.length}/{MAX_TICKERS}
                    </span>
                  </div>

                  <div
                    className={`flex min-h-14 flex-wrap items-center gap-2 rounded-xl border bg-white/70 px-3 py-2 transition focus-within:border-[#278a60] focus-within:ring-4 focus-within:ring-[#278a60]/10 ${
                      errors.tickers
                        ? "border-[#c74848] ring-4 ring-[#c74848]/10"
                        : "border-[#cbd1cb]"
                    }`}
                    onClick={() => inputRef.current?.focus()}
                  >
                    {tickers.map((ticker) => (
                      <span
                        key={ticker}
                        className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-[#d9f2e4] px-2.5 text-sm font-bold tracking-[0.04em] text-[#17613f]"
                      >
                        {ticker}
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            removeTicker(ticker);
                          }}
                          aria-label={`Remove ${ticker}`}
                          className="grid h-5 w-5 place-items-center rounded-full text-[#39765a] transition hover:bg-[#bde5cf] hover:text-[#124b32] focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[#278a60]"
                        >
                          <svg
                            aria-hidden="true"
                            viewBox="0 0 16 16"
                            className="h-3 w-3"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <path d="M4 4l8 8M12 4l-8 8" />
                          </svg>
                        </button>
                      </span>
                    ))}
                    <input
                      ref={inputRef}
                      id="ticker-input"
                      type="text"
                      value={tickerInput}
                      onChange={(event) => handleTickerChange(event.target.value)}
                      onKeyDown={handleTickerKeyDown}
                      disabled={tickers.length >= MAX_TICKERS}
                      aria-invalid={Boolean(errors.tickers)}
                      aria-describedby={
                        errors.tickers ? "ticker-help ticker-error" : "ticker-help"
                      }
                      aria-label="Add a ticker symbol"
                      autoCapitalize="characters"
                      autoComplete="off"
                      placeholder={tickers.length ? "Add another" : "e.g. AAPL"}
                      className="h-8 min-w-28 flex-1 bg-transparent px-1 text-sm font-semibold tracking-[0.04em] text-[#17231f] uppercase outline-none placeholder:font-normal placeholder:tracking-normal placeholder:text-[#98a19d] disabled:cursor-not-allowed"
                    />
                  </div>
                  <p id="ticker-help" className="mt-2 text-xs text-[#7a8580]">
                    Press Enter or comma to add a ticker.
                  </p>
                  {errors.tickers && (
                    <p id="ticker-error" className="mt-2 text-sm text-[#a83232]">
                      {errors.tickers}
                    </p>
                  )}
                </div>

                {errors.form && (
                  <div
                    role="alert"
                    className="rounded-xl border border-[#e4b7b2] bg-[#fff1ef] px-4 py-3 text-sm leading-5 text-[#8f2f28]"
                  >
                    {errors.form}
                  </div>
                )}

                {isSuccess && (
                  <div
                    role="status"
                    className="flex items-start gap-3 rounded-xl border border-[#aed9be] bg-[#e9f7ee] px-4 py-3.5 text-sm text-[#155b38]"
                  >
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 20 20"
                      className="mt-0.5 h-5 w-5 shrink-0"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <circle cx="10" cy="10" r="8" />
                      <path d="M6.5 10l2.2 2.2 4.8-5" />
                    </svg>
                    <div>
                      <p className="font-semibold">Request received.</p>
                      <p className="mt-0.5">Check your inbox in a minute or two</p>
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="group flex h-13 w-full items-center justify-center gap-2 rounded-xl bg-[#123f34] px-5 text-sm font-bold text-white shadow-[0_8px_24px_rgba(18,63,52,0.18)] transition hover:bg-[#0d332a] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#278a60] disabled:cursor-wait disabled:opacity-70"
                >
                  {isLoading ? (
                    <>
                      <span
                        aria-hidden="true"
                        className="h-4 w-4 animate-spin rounded-full border-2 border-white/35 border-t-white"
                      />
                      Preparing your brief…
                    </>
                  ) : (
                    <>
                      Send my market brief
                      <svg
                        aria-hidden="true"
                        viewBox="0 0 20 20"
                        className="h-4 w-4 transition group-hover:translate-x-0.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      >
                        <path d="M4 10h12M11 5l5 5-5 5" />
                      </svg>
                    </>
                  )}
                </button>
              </form>

              <p className="mt-5 text-center text-xs leading-5 text-[#87908c]">
                Your email is only used to deliver this summary.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
