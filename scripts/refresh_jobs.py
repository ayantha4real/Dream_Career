"""
DreamCareer — Automated job registry refresh.

Runs all Scrapy spiders (xpressjobs + topjobs) and upserts every
listing into database/dreamcareer.db via the SQLite pipeline.

Usage:
    venv\Scripts\python scripts\refresh_jobs.py              # all spiders
    venv\Scripts\python scripts\refresh_jobs.py --spider topjobs
"""

import argparse
import os
import sqlite3
import subprocess
import sys
import time


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

SCRAPER_DIR = os.path.join(PROJECT_ROOT, "job_scraper")

DATABASE_PATH = os.path.join(
    PROJECT_ROOT, "database", "dreamcareer.db"
)

SPIDERS = ["xpressjobs", "topjobs"]


def count_jobs():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    counts = {}

    for source in ["all"] + SPIDERS:

        if source == "all":
            cursor.execute("SELECT COUNT(*) FROM jobs")
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM jobs WHERE source = ?",
                (source,)
            )

        counts[source] = cursor.fetchone()[0]

    connection.close()

    return counts


def run_spider(name):
    command = [
        sys.executable, "-m", "scrapy", "crawl", name,
        "-s", "LOG_LEVEL=INFO",
    ]

    print(f"\n{'=' * 60}")
    print(f"RUNNING SPIDER: {name}")
    print(f"{'=' * 60}")

    started = time.time()

    result = subprocess.run(
        command,
        cwd=SCRAPER_DIR,
    )

    elapsed = time.time() - started

    status = "OK" if result.returncode == 0 else "FAILED"

    print(f"\nSpider '{name}' finished in {elapsed:.0f}s — {status}")

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Refresh the DreamCareer job registry"
    )

    parser.add_argument(
        "--spider",
        choices=SPIDERS,
        help="Run only this spider instead of all",
    )

    args = parser.parse_args()

    selected = [args.spider] if args.spider else SPIDERS

    before = count_jobs()

    print("Jobs before refresh:")
    for source, count in before.items():
        print(f"  {source:12s} {count}")

    results = {}

    for name in selected:
        results[name] = run_spider(name)

    after = count_jobs()

    print(f"\n{'=' * 60}")
    print("REFRESH SUMMARY")
    print(f"{'=' * 60}")
    print("Jobs after refresh:")
    for source, count in after.items():
        delta = count - before[source]
        sign = f"(+{delta})" if delta >= 0 else f"({delta})"
        print(f"  {source:12s} {count} {sign}")

    failed = [
        name for name, ok in results.items() if not ok
    ]

    if failed:
        print(f"\nWARNING: spiders failed: {', '.join(failed)}")
        sys.exit(1)

    print("\nAll spiders completed successfully.")


if __name__ == "__main__":
    main()
