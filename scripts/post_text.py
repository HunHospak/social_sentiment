"""Generate a ready-to-post social snippet from the latest feed."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    feed = json.loads((ROOT / "out" / "social_sentiment.json").read_text(encoding="utf-8"))
    d = feed["data"]
    lines = [f"Retail buzz — {d['as_of']} (StockTwits)"]
    lines.append("Most bullish: " + ", ".join("$" + t for t in d.get("most_bullish", [])))
    lines.append("Most bearish: " + ", ".join("$" + t for t in d.get("most_bearish", [])))
    lines.append("Most talked-about: " + ", ".join("$" + t for t in d.get("most_buzzed", [])))
    lines.append("Crowd chatter, often contrarian · not investment advice · arkenlabs.eu")
    text = "\n".join(lines)
    (ROOT / "out" / "post.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
