#!/usr/bin/env python3
"""Concurrent load test for the Splash site. Zero dependencies (stdlib only).

Warms the cache, fires N requests at a given concurrency across a page mix, and reports latency
percentiles, throughput and success rate. Writes a Markdown summary to $GITHUB_STEP_SUMMARY when run in
Actions. Configure via env: TARGET, CONCURRENCY, TOTAL, WARM (1/0)."""
import os
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

TARGET = os.environ.get("TARGET", "https://splash-web-chi.vercel.app").rstrip("/")
CONCURRENCY = int(os.environ.get("CONCURRENCY", "20"))
TOTAL = int(os.environ.get("TOTAL", "300"))
WARM = os.environ.get("WARM", "1") == "1"
PAGES = ["/", "/pricing", "/menu", "/gallery", "/contact", "/business", "/about", "/locations/kuils-river"]


def hit(path):
    t0 = time.time()
    try:
        req = urllib.request.Request(TARGET + path, headers={"User-Agent": "splash-perf"})
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read()
            return (path, r.status, time.time() - t0, None)
    except urllib.error.HTTPError as e:
        return (path, e.code, time.time() - t0, None)
    except Exception as e:  # noqa: BLE001 - report any failure mode
        return (path, None, time.time() - t0, type(e).__name__)


def main():
    print(f"target={TARGET} concurrency={CONCURRENCY} total={TOTAL} warm={WARM}")
    if WARM:
        print("warming cache...")
        for p in PAGES:
            hit(p)

    reqs = [PAGES[i % len(PAGES)] for i in range(TOTAL)]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        results = list(ex.map(hit, reqs))
    wall = time.time() - t0

    lat = sorted(r[2] for r in results)
    ok = sum(1 for r in results if r[1] == 200)
    errs = [r for r in results if r[1] != 200]

    def pct(p):
        return lat[min(len(lat) - 1, int(len(lat) * p))] * 1000

    rows = [
        ("requests", f"{TOTAL} @ {CONCURRENCY} concurrent"),
        ("wall time", f"{wall:.2f} s"),
        ("throughput", f"{TOTAL / wall:.1f} req/s"),
        ("success", f"{ok}/{TOTAL} ({100 * ok / TOTAL:.1f}%)"),
        ("latency min", f"{lat[0] * 1000:.0f} ms"),
        ("latency p50", f"{pct(0.50):.0f} ms"),
        ("latency p90", f"{pct(0.90):.0f} ms"),
        ("latency p95", f"{pct(0.95):.0f} ms"),
        ("latency p99", f"{pct(0.99):.0f} ms"),
        ("latency max", f"{lat[-1] * 1000:.0f} ms"),
    ]
    for k, v in rows:
        print(f"  {k:14}: {v}")
    if errs:
        print(f"  errors        : {Counter((e[1], e[3]) for e in errs)}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(f"## Load test — {TARGET}\n\n")
            f.write("| metric | value |\n|---|---|\n")
            for k, v in rows:
                f.write(f"| {k} | {v} |\n")
            if errs:
                f.write(f"\n**errors:** {Counter((e[1], e[3]) for e in errs)}\n")

    # Fail the job if too many requests errored — turns this into a real regression gate.
    if ok / TOTAL < 0.98:
        raise SystemExit(f"success rate {100 * ok / TOTAL:.1f}% below 98% threshold")


if __name__ == "__main__":
    main()
