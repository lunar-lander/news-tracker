#!/usr/bin/env python3
"""
Database Setup Script
Initializes the database schema and seeds RSS sources from config.
Run this after starting PostgreSQL for the first time.

Usage:
    cd backend
    python -m scripts.setup_database
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine, async_session_maker
from app.config import load_rss_sources

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def check_connection():
    """Verify database connectivity"""
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def check_schema():
    """Check if schema is already applied (via docker-entrypoint-initdb.d)"""
    async with async_session_maker() as session:
        result = await session.execute(
            text(
                "SELECT EXISTS ("
                "  SELECT FROM information_schema.tables "
                "  WHERE table_name = 'rss_sources'"
                ")"
            )
        )
        return result.scalar()


async def apply_schema():
    """Apply schema from schema.sql if not already present"""
    backend_root = Path(__file__).resolve().parent.parent
    candidates = [
        backend_root / "database" / "schema.sql",        # Docker: /app/database/schema.sql
        backend_root.parent / "database" / "schema.sql",  # Local dev
    ]
    schema_path = next((p for p in candidates if p.exists()), None)

    if schema_path is None:
        logger.error(f"Schema file not found (searched: {candidates})")
        sys.exit(1)

    schema_sql = schema_path.read_text(encoding="utf-8")

    # Split by semicolons and execute each statement
    # (skip empty statements and comments-only blocks)
    async with engine.begin() as conn:
        # Execute the whole schema as one block — PostgreSQL handles this fine
        await conn.execute(text(schema_sql))

    logger.info("✅ Database schema applied successfully")


async def seed_rss_sources():
    """Seed RSS sources from config/rss-sources.yaml"""
    from sqlalchemy.dialects.postgresql import insert
    from app.models.rss import RSSSource
    from datetime import datetime, timezone

    sources_config = load_rss_sources()
    logger.info(f"Seeding {len(sources_config)} RSS sources from config...")

    async with async_session_maker() as session:
        for source_data in sources_config:
            stmt = (
                insert(RSSSource)
                .values(
                    name=source_data["name"],
                    url=source_data["url"],
                    category=source_data.get("category"),
                    language=source_data.get("language"),
                    region=source_data.get("region"),
                    priority=source_data.get("priority"),
                    refresh_interval=source_data.get("refresh_interval", 300),
                    enabled=source_data.get("enabled", True),
                )
                .on_conflict_do_update(
                    index_elements=["url"],
                    set_=dict(
                        name=source_data["name"],
                        category=source_data.get("category"),
                        language=source_data.get("language"),
                        region=source_data.get("region"),
                        priority=source_data.get("priority"),
                        refresh_interval=source_data.get("refresh_interval", 300),
                        enabled=source_data.get("enabled", True),
                        updated_at=datetime.now(timezone.utc),
                    ),
                )
            )
            await session.execute(stmt)

        await session.commit()
        logger.info("✅ RSS sources seeded successfully")


async def main():
    """Main setup entry point"""
    logger.info("=" * 60)
    logger.info("India News Tracker - Database Setup")
    logger.info("=" * 60)

    # Step 1: Check connection
    if not await check_connection():
        logger.error("Cannot connect to database. Is PostgreSQL running?")
        logger.error("  Start it with: make dev-db")
        sys.exit(1)

    # Step 2: Check/apply schema
    schema_exists = await check_schema()
    if schema_exists:
        logger.info("✅ Database schema already exists (applied via Docker init)")
    else:
        logger.info("Applying database schema...")
        await apply_schema()

    # Step 3: Seed RSS sources
    await seed_rss_sources()

    logger.info("=" * 60)
    logger.info("✅ Database setup complete!")
    logger.info("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
