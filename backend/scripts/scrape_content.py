#!/usr/bin/env python3
"""
Article Content Scraper
Fetches full article content from RSS entry URLs and extracts clean text.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

sys.path.append(str(Path(__file__).parent.parent))

from app.database import async_session_maker
from app.models.rss import RSSEntry
from app.models.article import Article
from app.models.processing_log import ProcessingLog

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request timeout and headers
TIMEOUT = 10
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_article_html(url: str) -> Optional[str]:
    """Fetch HTML content from URL"""
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def extract_text_from_html(html: str, url: str) -> Optional[str]:
    """Extract clean text from HTML"""
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
            script.decompose()

        # Try to find main content area - common patterns
        main_content = None

        # Try article tag first (semantic HTML5)
        article = soup.find('article')
        if article:
            main_content = article

        # Try common content div classes/ids
        if not main_content:
            for selector in [
                {'class': 'article-body'},
                {'class': 'story-body'},
                {'class': 'post-content'},
                {'class': 'entry-content'},
                {'class': 'content'},
                {'id': 'article-content'},
                {'id': 'story-content'},
            ]:
                main_content = soup.find('div', selector)
                if main_content:
                    break

        # Fallback to body if nothing found
        if not main_content:
            main_content = soup.find('body')

        if not main_content:
            logger.warning(f"Could not find main content in {url}")
            return None

        # Extract text
        text = main_content.get_text(separator='\n', strip=True)

        # Clean up multiple newlines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = '\n\n'.join(lines)

        # Basic validation
        word_count = len(clean_text.split())
        if word_count < 50:
            logger.warning(f"Extracted text too short ({word_count} words) for {url}")
            return None

        logger.info(f"Extracted {word_count} words from {url}")
        return clean_text

    except Exception as e:
        logger.error(f"Error extracting text from {url}: {e}")
        return None


def detect_language(text: str) -> str:
    """
    Simple language detection - just check for Hindi/Devanagari script
    For production, use langdetect or lingua library
    """
    # Check for Hindi/Devanagari characters
    hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
    total_chars = len([c for c in text if c.isalpha()])

    if total_chars > 0 and (hindi_chars / total_chars) > 0.3:
        return 'hindi'

    return 'english'


async def scrape_article(entry: RSSEntry) -> Dict[str, Any]:
    """Scrape a single article"""
    result = {
        'entry_id': entry.id,
        'success': False,
        'error_message': None,
    }

    try:
        # Fetch HTML
        html = fetch_article_html(entry.link)
        if not html:
            result['error_message'] = "Failed to fetch HTML"
            return result

        # Extract text
        extracted_text = extract_text_from_html(html, entry.link)
        if not extracted_text:
            result['error_message'] = "Failed to extract text"
            return result

        # Detect language
        language = detect_language(extracted_text)

        # Count words
        word_count = len(extracted_text.split())

        # Store in database
        async with async_session_maker() as session:
            article = Article(
                rss_entry_id=entry.id,
                full_text=html[:50000],  # Store first 50k chars of HTML
                extracted_text=extracted_text,
                word_count=word_count,
                language=language,
                scraped_at=datetime.now(timezone.utc),
                scraping_method='beautifulsoup',
                scraping_success=True,
            )
            session.add(article)

            # Update RSS entry status
            entry.processing_status = 'scraped'
            await session.commit()

            result['success'] = True
            result['article_id'] = article.id
            logger.info(f"Successfully scraped article {article.id} for entry {entry.id}")

        return result

    except Exception as e:
        logger.error(f"Error scraping entry {entry.id}: {e}")
        result['error_message'] = str(e)

        # Update entry status to failed
        try:
            async with async_session_maker() as session:
                result_query = await session.execute(
                    select(RSSEntry).where(RSSEntry.id == entry.id)
                )
                entry_update = result_query.scalar_one_or_none()
                if entry_update:
                    entry_update.processing_status = 'scraping_failed'
                    await session.commit()
        except Exception as update_error:
            logger.error(f"Failed to update entry status: {update_error}")

        return result


async def scrape_pending_articles(batch_size: int = 50):
    """Scrape all pending articles"""
    logger.info("Starting article scraping job...")

    # Create processing log
    log_id = None
    async with async_session_maker() as session:
        log = ProcessingLog(
            job_type="content_scraping",
            status="running",
            metadata={"started_at": datetime.now(timezone.utc).isoformat()}
        )
        session.add(log)
        await session.commit()
        log_id = log.id

    total_processed = 0
    total_success = 0
    total_failed = 0

    # Fetch pending entries in batches
    async with async_session_maker() as session:
        result = await session.execute(
            select(RSSEntry)
            .where(RSSEntry.processing_status == 'pending')
            .limit(batch_size)
        )
        entries = result.scalars().all()

        logger.info(f"Found {len(entries)} pending entries to scrape")

        for entry in entries:
            result = await scrape_article(entry)
            total_processed += 1

            if result['success']:
                total_success += 1
            else:
                total_failed += 1

            # Small delay to be respectful to servers
            await asyncio.sleep(0.5)

    # Update processing log
    async with async_session_maker() as session:
        result_query = await session.execute(
            select(ProcessingLog).where(ProcessingLog.id == log_id)
        )
        log = result_query.scalar_one_or_none()

        if log:
            log.completed_at = datetime.now(timezone.utc)
            log.status = "completed"
            log.items_processed = total_processed
            log.items_failed = total_failed
            log.meta_data = {
                "articles_scraped": total_success,
                "articles_failed": total_failed,
            }
            await session.commit()

    logger.info(f"Scraping completed: {total_success} success, {total_failed} failed out of {total_processed} total")


async def main():
    """Main entry point"""
    try:
        await scrape_pending_articles(batch_size=50)
    except Exception as e:
        logger.error(f"Article scraping job failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
