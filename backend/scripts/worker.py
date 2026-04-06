#!/usr/bin/env python3
"""
Pipeline Worker
Runs fetch, scrape, and classify as independent concurrent loops.
Each loop runs on its own interval. Classification polls frequently
and no-ops when there is nothing to classify.
Designed to run as a long-lived Docker container alongside the API.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.fetch_rss import fetch_all_feeds, seed_rss_sources
from scripts.scrape_content import scrape_pending_articles
from scripts.classify_articles import classify_pending_articles

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Intervals in seconds (configurable via env)
FETCH_INTERVAL = int(os.environ.get("FETCH_INTERVAL", "300"))
SCRAPE_INTERVAL = int(os.environ.get("SCRAPE_INTERVAL", "60"))
CLASSIFY_POLL = int(os.environ.get("CLASSIFY_POLL_INTERVAL", "10"))
SCRAPE_BATCH = int(os.environ.get("SCRAPE_BATCH_SIZE", "100"))
CLASSIFY_BATCH = int(os.environ.get("CLASSIFY_BATCH_SIZE", "50"))


async def run_loop(name: str, coro, interval: int, quiet: bool = False, **kwargs):
    """Run a coroutine in a loop with a fixed interval.

    If *quiet* is True, only log when the cycle actually did work
    (useful for high-frequency polling loops like classify).
    """
    while True:
        try:
            if not quiet:
                logger.info(f"[{name}] Starting cycle")
            result = await coro(**kwargs)
            if not quiet:
                logger.info(f"[{name}] Cycle complete, sleeping {interval}s")
        except Exception as e:
            logger.error(f"[{name}] Error: {e}", exc_info=True)
        await asyncio.sleep(interval)


async def main():
    # Seed RSS sources on first start
    try:
        await seed_rss_sources()
    except Exception as e:
        logger.error(f"Failed to seed RSS sources: {e}")

    logger.info(
        f"Worker starting — fetch every {FETCH_INTERVAL}s, "
        f"scrape every {SCRAPE_INTERVAL}s, "
        f"classify polls every {CLASSIFY_POLL}s"
    )

    await asyncio.gather(
        run_loop("fetch", fetch_all_feeds, FETCH_INTERVAL),
        run_loop(
            "scrape",
            scrape_pending_articles,
            SCRAPE_INTERVAL,
            batch_size=SCRAPE_BATCH,
        ),
        run_loop(
            "classify",
            classify_pending_articles,
            CLASSIFY_POLL,
            quiet=True,
            batch_size=CLASSIFY_BATCH,
        ),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped")
