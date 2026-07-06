"""Orchestration: ingest -> compute -> validate(schema) -> write out/."""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Optional StockTwits token from .env (local) or CI secret (same var name).
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:
    pass

from providers import get_stocktwits  # noqa: E402
from compute import analyze, summarize  # noqa: E402


def load_config() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))


def load_schema() -> dict:
    return json.loads((ROOT / "schema.json").read_text(encoding="utf-8"))


def build(cfg: dict) -> dict:
    token = os.environ.get(cfg.get("token_env", "")) or None
    delay = float(cfg.get("request_delay_sec", 1.0))
    tickers = list(cfg["tickers"])
    rows = []
    failures = 0
    for i, t in enumerate(tickers):
        raw = get_stocktwits(t, token)
        if raw is None:
            failures += 1
        else:
            rows.append(analyze(t, raw, int(cfg["min_messages"])))
        if i < len(tickers) - 1:
            time.sleep(delay)

    rows.sort(key=lambda r: -r["buzz"])
    summary = summarize(rows)

    if not rows:
        status, notes = "unavailable", "stocktwits unavailable"
    elif failures > 0:
        status, notes = "partial", f"{failures} tickers failed"
    else:
        status, notes = "active", None

    data = {
        "as_of": dt.date.today().isoformat(),
        "source": cfg.get("source", "stocktwits"),
        "count": len(rows),
        "tickers": rows,
        "disclaimer": "Aggregated retail social chatter — noisy and often contrarian, not a signal.",
    }
    data.update(summary)

    feed = {
        "service": cfg["service"],
        "schema_version": str(cfg["schema_version"]),
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "ttl_hours": cfg["ttl_hours"],
        "data": data,
    }
    if notes:
        feed["notes"] = notes
    return feed


def main() -> None:
    cfg = load_config()
    feed = build(cfg)
    jsonschema.validate(feed, load_schema())
    out = ROOT / "out"
    (out / "history").mkdir(parents=True, exist_ok=True)
    payload = json.dumps(feed, indent=2)
    (out / "social_sentiment.json").write_text(payload, encoding="utf-8")
    (out / "history" / f"{feed['data']['as_of']}.json").write_text(payload, encoding="utf-8")
    print(f"[social_sentiment] status={feed['status']} tickers={feed['data']['count']}")


if __name__ == "__main__":
    main()
