# dinare-perf

Load / performance testing for the Splash site, run from **free** GitHub Actions (this repo is public, so
Actions minutes are unlimited and unmetered).

## Run a test

- **On demand:** Actions tab → **load-test** → **Run workflow** → optionally set the target URL, concurrency,
  and total requests → Run. Results (throughput, success rate, latency p50/p90/p95/p99) appear in the run's
  **Summary**.
- **Automatically:** a light run every Monday 06:00 UTC as a regression check.

Locally:

```bash
TARGET=https://splash-web-chi.vercel.app CONCURRENCY=20 TOTAL=300 python3 load-test.py
```

## What it does

`load-test.py` (stdlib only, no dependencies) warms the cache, then fires `TOTAL` requests at `CONCURRENCY`
across a representative page mix, and reports latency percentiles, throughput, and success rate. It **fails
the job if the success rate drops below 98%**, so it doubles as an availability gate.

## Honest caveats

- **Location:** GitHub's runners are in Microsoft Azure datacenters, not South Africa. So these numbers are
  great for **regression detection** ("did a change make it slower / did it start erroring under load?") and
  **concurrency behaviour**, but they are **not** real-user latency for a visitor in Cape Town. For that, use
  Vercel Analytics, Lighthouse, or WebPageTest from a SA location.
- **Be a good citizen:** this points at your own site on free tiers. Keep the schedule infrequent and the
  request counts modest — a load test is not a stress-to-failure attack. Don't crank `TOTAL`/`CONCURRENCY` to
  abusive levels.
- **Cache warming:** the script warms the cache first, so it measures steady-state (like a trafficked site),
  not the cold-start of a fresh deploy.
