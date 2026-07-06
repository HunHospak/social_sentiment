"""Pure logic — no I/O, unit-testable.

Aggregated retail social sentiment. Note: crowd sentiment is noisy and often contrarian;
this is engagement / context, not a signal. The feed and the Arken panel say so.
"""
from __future__ import annotations


def sentiment_score(bullish: int, bearish: int) -> float | None:
    total = bullish + bearish
    if total == 0:
        return None
    return round((bullish - bearish) / total, 3)  # -1 (all bear) .. +1 (all bull)


def label(score: float | None, rated: int, min_messages: int) -> str:
    if score is None or rated < min_messages:
        return "insufficient"
    if score >= 0.25:
        return "bullish"
    if score <= -0.25:
        return "bearish"
    return "mixed"


def analyze(ticker: str, raw: dict, min_messages: int) -> dict:
    bull = int(raw.get("bullish", 0))
    bear = int(raw.get("bearish", 0))
    total = int(raw.get("total", 0))
    rated = bull + bear
    sc = sentiment_score(bull, bear)
    return {
        "ticker": ticker,
        "bullish": bull,
        "bearish": bear,
        "rated": rated,
        "buzz": total,           # recent message count sampled (proxy for chatter)
        "sentiment_score": sc,
        "label": label(sc, rated, min_messages),
    }


def summarize(rows: list[dict]) -> dict:
    scored = [r for r in rows if r["label"] in ("bullish", "bearish", "mixed")]
    by_buzz = sorted(scored, key=lambda r: -r["buzz"])
    by_score = sorted([r for r in scored if r["sentiment_score"] is not None],
                      key=lambda r: -r["sentiment_score"])
    return {
        "most_buzzed": [r["ticker"] for r in by_buzz[:3]],
        "most_bullish": [r["ticker"] for r in by_score[:3]],
        "most_bearish": [r["ticker"] for r in by_score[::-1][:3]],
    }
