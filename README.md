# social_sentiment

Independent ArkenLabs satellite service. Aggregates **existing** retail social chatter (StockTwits
public symbol streams) into a bullish/bearish sentiment score and a "buzz" count per ticker — no
voting, no accounts, no bot problem.

**Honest scope:** crowd sentiment is noisy and often *contrarian*; this is engagement / context, not
a signal. The feed and the Arken panel both say so.

## Why not a voting page?
The original "let people vote daily" idea has a cold-start problem (empty without users) and a hard
bot-defense problem. Aggregating what the crowd *already* says avoids both and is meaningful from day
one. A voting/community feature can come later, once there's an audience.

## Run locally
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# optional, raises StockTwits rate limits:
# echo "STOCKTWITS_TOKEN=..." > .env
python src/build_feed.py       # writes out/social_sentiment.json + history
python scripts/post_text.py    # writes out/post.txt
```

## Configure
`config.yaml`: `tickers` (retail-heavy names have the most chatter), `min_messages`,
`request_delay_sec` (be polite to the API), `token_env` (optional token var name).

## Deploy
`.github/workflows/publish.yml` runs weekday cron, builds, publishes `out/` to GitHub Pages:
`https://<user>.github.io/social_sentiment/social_sentiment.json`. Optionally set the `STOCKTWITS_TOKEN`
repo secret.

## Future sources
Reddit (r/wallstreetbets, r/stocks) via OAuth and X/Twitter (paid) can be added as extra providers,
each folded into the same bullish/bearish/buzz aggregation.

## Independence
Knows nothing about Arken. Arken knows only the feed URL + the shared schema.
