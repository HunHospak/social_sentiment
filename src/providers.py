"""Data provider for social_sentiment — StockTwits public symbol streams."""
from __future__ import annotations

import requests

_UA = {"User-Agent": "arkenlabs-social/1.0"}
_URL = "https://api.stocktwits.com/api/2/streams/symbol/{sym}.json"


def get_stocktwits(ticker: str, token: str | None = None, timeout: int = 10) -> dict | None:
    """Bullish/bearish counts from the latest StockTwits messages for a symbol.

    Returns {"bullish", "bearish", "total"} or None on failure / rate limit.
    """
    params = {}
    if token:
        params["access_token"] = token
    try:
        r = requests.get(_URL.format(sym=ticker), params=params, headers=_UA, timeout=timeout)
        if r.status_code != 200:
            return None
        messages = r.json().get("messages") or []
        bull = 0
        bear = 0
        for m in messages:
            ent = m.get("entities") or {}
            sent = ent.get("sentiment") or {}
            basic = sent.get("basic") if isinstance(sent, dict) else None
            if basic == "Bullish":
                bull += 1
            elif basic == "Bearish":
                bear += 1
        return {"bullish": bull, "bearish": bear, "total": len(messages)}
    except Exception:
        return None
