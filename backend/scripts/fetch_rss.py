#!/usr/bin/env python3
"""
RSS Feed Fetcher
Fetches RSS feeds from configured sources and stores new entries in the database.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
import feedparser
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import load_rss_sources
from app.database import async_session_maker
from app.models.rss import RSSSource, RSSEntry
from app.models.processing_log import ProcessingLog

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_content_hash(title: str, link: str) -> str:
    """Generate a hash for deduplication"""
    content = f"{title}{link}"
    return hashlib.sha256(content.encode()).hexdigest()


async def seed_rss_sources():
    """Seed RSS sources from config into database"""
    logger.info("Seeding RSS sources from config...")

    sources_config = load_rss_sources()
    logger.info(f"Loaded {len(sources_config)} RSS sources from config")

    async with async_session_maker() as session:
        for source_data in sources_config:
            # Use PostgreSQL's INSERT ... ON CONFLICT DO UPDATE
            stmt = insert(RSSSource).values(
                name=source_data['name'],
                url=source_data['url'],
                category=source_data.get('category'),
                language=source_data.get('language'),
                region=source_data.get('region'),
                priority=source_data.get('priority'),
                refresh_interval=source_data.get('refresh_interval', 300),
                enabled=source_data.get('enabled', True),
            ).on_conflict_do_update(
                index_elements=['url'],
                set_=dict(
                    name=source_data['name'],
                    category=source_data.get('category'),
                    language=source_data.get('language'),
                    region=source_data.get('region'),
                    priority=source_data.get('priority'),
                    refresh_interval=source_data.get('refresh_interval', 300),
                    enabled=source_data.get('enabled', True),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            await session.execute(stmt)

        await session.commit()
        logger.info("RSS sources seeded successfully")


async def fetch_feed(source: RSSSource) -> List[Dict[str, Any]]:
    """Fetch and parse a single RSS feed"""
    logger.info(f"Fetching feed: {source.name} ({source.url})")

    try:
        # Parse RSS feed
        feed = feedparser.parse(source.url)

        if feed.bozo:  # Check if feed has errors
            logger.warning(f"Feed {source.name} has parsing errors: {feed.bozo_exception}")

        entries = []
        for entry in feed.entries:
            # Extract published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)

            # Generate GUID
            guid = entry.get('id') or entry.get('link') or generate_content_hash(
                entry.get('title', ''),
                entry.get('link', '')
            )

            # Generate content hash for deduplication
            content_hash = generate_content_hash(
                entry.get('title', ''),
                entry.get('link', '')
            )

            entry_data = {
                'source_id': source.id,
                'guid': guid,
                'title': entry.get('title', ''),
                'description': entry.get('description') or entry.get('summary', ''),
                'link': entry.get('link', ''),
                'published_at': published_at,
                'author': entry.get('author', ''),
                'content_hash': content_hash,
                'raw_data': {
                    'title': entry.get('title'),
                    'link': entry.get('link'),
                    'description': entry.get('description'),
                    'summary': entry.get('summary'),
                    'author': entry.get('author'),
                    'published': entry.get('published'),
                    'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else [],
                },
                'processing_status': 'pending',
            }

            entries.append(entry_data)

        logger.info(f"Fetched {len(entries)} entries from {source.name}")
        return entries

    except Exception as e:
        logger.error(f"Error fetching feed {source.name}: {e}")
        return []


async def store_entries(entries: List[Dict[str, Any]]) -> int:
    """Store RSS entries in database, handling duplicates"""
    if not entries:
        return 0

    new_count = 0
    async with async_session_maker() as session:
        for entry_data in entries:
            # Use INSERT ... ON CONFLICT DO NOTHING for deduplication
            stmt = insert(RSSEntry).values(**entry_data).on_conflict_do_nothing(
                index_elements=['guid']
            )
            result = await session.execute(stmt)

            if result.rowcount > 0:
                new_count += 1

        await session.commit()

    logger.info(f"Stored {new_count} new entries (skipped {len(entries) - new_count} duplicates)")
    return new_count


async def update_source_status(source_id: int, success: bool):
    """Update source fetch status"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(RSSSource).where(RSSSource.id == source_id)
        )
        source = result.scalar_one_or_none()

        if source:
            source.last_fetched_at = datetime.now(timezone.utc)

            if success:
                source.last_success_at = datetime.now(timezone.utc)
                source.consecutive_failures = 0
            else:
                source.consecutive_failures += 1

            await session.commit()


async def fetch_all_feeds():
    """Fetch all enabled RSS feeds"""
    logger.info("Starting RSS feed fetch job...")

    # Create processing log
    log_id = None
    async with async_session_maker() as session:
        log = ProcessingLog(
            job_type="rss_fetch",
            status="running",
            metadata={"started_at": datetime.now(timezone.utc).isoformat()}
        )
        session.add(log)
        await session.commit()
        log_id = log.id

    # Fetch enabled sources
    total_processed = 0
    total_failed = 0
    total_new_entries = 0

    async with async_session_maker() as session:
        result = await session.execute(
            select(RSSSource).where(RSSSource.enabled == True)
        )
        sources = result.scalars().all()

        logger.info(f"Found {len(sources)} enabled RSS sources")

        for source in sources:
            try:
                entries = await fetch_feed(source)
                new_count = await store_entries(entries)

                await update_source_status(source.id, success=True)

                total_processed += 1
                total_new_entries += new_count

            except Exception as e:
                logger.error(f"Failed to process source {source.name}: {e}")
                await update_source_status(source.id, success=False)
                total_failed += 1

    # Update processing log
    async with async_session_maker() as session:
        result = await session.execute(
            select(ProcessingLog).where(ProcessingLog.id == log_id)
        )
        log = result.scalar_one_or_none()

        if log:
            log.completed_at = datetime.now(timezone.utc)
            log.status = "completed"
            log.items_processed = total_processed
            log.items_failed = total_failed
            log.metadata = {
                "sources_processed": total_processed,
                "sources_failed": total_failed,
                "new_entries": total_new_entries,
            }
            await session.commit()

    logger.info(f"RSS fetch completed: {total_processed} sources processed, {total_failed} failed, {total_new_entries} new entries")


async def main():
    """Main entry point"""
    try:
        # First, seed RSS sources from config
        await seed_rss_sources()

        # Then fetch all feeds
        await fetch_all_feeds()

    except Exception as e:
        logger.error(f"RSS fetch job failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
