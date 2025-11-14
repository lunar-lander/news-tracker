#!/usr/bin/env python3
"""
LLM Article Classifier
Classifies articles using configured LLM providers (Gemini, Claude, etc.)
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import re

from sqlalchemy import select

sys.path.append(str(Path(__file__).parent.parent))

from app.config import load_llm_config, load_tags_config, settings
from app.database import async_session_maker
from app.models.article import Article
from app.models.rss import RSSEntry, RSSSource
from app.models.classification import Classification
from app.models.news_event import NewsEvent
from app.models.processing_log import ProcessingLog

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMClassifier:
    """Handles LLM classification with multi-provider support"""

    def __init__(self):
        self.llm_config = load_llm_config()
        self.tags_config = load_tags_config()
        self.classification_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load classification prompt template"""
        prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'classification.txt'
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load classification prompt: {e}")
            raise

    def _get_enabled_tags(self) -> List[str]:
        """Get list of enabled tags"""
        enabled = self.tags_config.get('enabled_categories', [])
        return enabled

    def _build_prompt(self, article_text: str, headline: str) -> str:
        """Build classification prompt with article text"""
        enabled_tags = self._get_enabled_tags()
        tags_list = ', '.join(enabled_tags)

        prompt = self.classification_prompt.replace('{article_text}', article_text)
        prompt = prompt.replace('{headline}', headline)
        prompt = prompt.replace('{tags_list}', tags_list)

        return prompt

    async def classify_with_gemini(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Classify using Google Gemini"""
        try:
            import google.generativeai as genai

            api_key = settings.google_api_key
            if not api_key:
                logger.error("GOOGLE_API_KEY not set")
                return None

            genai.configure(api_key=api_key)

            model_name = self.llm_config['llm']['model']
            model = genai.GenerativeModel(model_name)

            logger.info(f"Calling Gemini API with model {model_name}")

            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': self.llm_config['llm']['temperature'],
                    'max_output_tokens': self.llm_config['llm']['max_tokens'],
                }
            )

            # Extract text from response
            response_text = response.text

            # Try to parse JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['_raw_response'] = response_text
                result['_tokens_used'] = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                return result
            else:
                logger.error("Could not find JSON in Gemini response")
                return None

        except Exception as e:
            logger.error(f"Gemini classification failed: {e}")
            return None

    async def classify_with_claude(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Classify using Anthropic Claude"""
        try:
            from anthropic import AsyncAnthropic

            api_key = settings.anthropic_api_key
            if not api_key:
                logger.error("ANTHROPIC_API_KEY not set")
                return None

            client = AsyncAnthropic(api_key=api_key)

            fallback_model = self.llm_config['llm'].get('fallback_model', 'claude-3-haiku-20240307')
            logger.info(f"Calling Claude API with model {fallback_model}")

            message = await client.messages.create(
                model=fallback_model,
                max_tokens=self.llm_config['llm']['max_tokens'],
                temperature=self.llm_config['llm']['temperature'],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Try to parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['_raw_response'] = response_text
                result['_tokens_used'] = message.usage.input_tokens + message.usage.output_tokens
                return result
            else:
                logger.error("Could not find JSON in Claude response")
                return None

        except Exception as e:
            logger.error(f"Claude classification failed: {e}")
            return None

    async def classify(self, article_text: str, headline: str) -> Optional[Dict[str, Any]]:
        """Classify article with fallback logic"""
        prompt = self._build_prompt(article_text, headline)

        # Try primary provider (Gemini)
        primary_provider = self.llm_config['llm']['provider']
        if primary_provider == 'google':
            result = await self.classify_with_gemini(prompt)
            if result:
                result['_provider'] = 'google'
                result['_model'] = self.llm_config['llm']['model']
                return result

        # Fallback to Claude
        logger.warning("Primary LLM failed, trying fallback (Claude)")
        result = await self.classify_with_claude(prompt)
        if result:
            result['_provider'] = 'anthropic'
            result['_model'] = self.llm_config['llm'].get('fallback_model', 'claude-3-haiku-20240307')
            return result

        logger.error("All LLM providers failed")
        return None


async def store_classification(
    article: Article,
    entry: RSSEntry,
    source: RSSSource,
    llm_result: Dict[str, Any]
) -> Optional[int]:
    """Store classification and create news event"""
    try:
        async with async_session_maker() as session:
            # Extract data from LLM result
            tags = llm_result.get('tags', [])
            tag_confidences = llm_result.get('tag_confidences', {})
            summary = llm_result.get('summary', '')
            severity = llm_result.get('severity', 'medium')
            incident_date_str = llm_result.get('incident_date')
            state = llm_result.get('state')
            city = llm_result.get('city')
            district = llm_result.get('district')
            location_confidence = llm_result.get('location_confidence', 0.0)
            persons = llm_result.get('persons', [])
            organizations = llm_result.get('organizations', [])

            # Parse incident date
            incident_date = None
            if incident_date_str:
                try:
                    incident_date = datetime.fromisoformat(incident_date_str).date()
                except:
                    pass

            # Calculate LLM cost (rough estimate)
            tokens_used = llm_result.get('_tokens_used', 0)
            cost_per_million = 0.075 if llm_result.get('_provider') == 'google' else 0.25
            cost_usd = (tokens_used / 1_000_000) * cost_per_million

            # Create classification record
            classification = Classification(
                article_id=article.id,
                llm_provider=llm_result.get('_provider'),
                llm_model=llm_result.get('_model'),
                classified_at=datetime.now(timezone.utc),
                tags=tags,
                tag_confidences=tag_confidences,
                summary=summary,
                severity=severity,
                incident_date=incident_date,
                state=state,
                city=city,
                district=district,
                location_confidence=location_confidence,
                persons=persons,
                organizations=organizations,
                raw_llm_response=llm_result,
                llm_tokens_used=tokens_used,
                llm_cost_usd=cost_usd,
            )
            session.add(classification)
            await session.flush()

            # Create denormalized news event
            primary_tag = tags[0] if tags else None
            news_event = NewsEvent(
                rss_entry_id=entry.id,
                article_id=article.id,
                classification_id=classification.id,
                headline=entry.title,
                summary=summary,
                source_name=source.name,
                source_url=entry.link,
                published_at=entry.published_at,
                incident_date=incident_date,
                primary_tag=primary_tag,
                all_tags=tags,
                severity=severity,
                state=state,
                city=city,
                region=source.region,
            )
            session.add(news_event)

            # Update RSS entry status
            entry.processing_status = 'completed'

            await session.commit()

            logger.info(f"Stored classification {classification.id} for article {article.id}")
            return classification.id

    except Exception as e:
        logger.error(f"Failed to store classification: {e}")
        return None


async def classify_article(article: Article, classifier: LLMClassifier) -> Dict[str, Any]:
    """Classify a single article"""
    result = {
        'article_id': article.id,
        'success': False,
        'error_message': None,
    }

    try:
        # Get RSS entry and source
        async with async_session_maker() as session:
            entry_result = await session.execute(
                select(RSSEntry).where(RSSEntry.id == article.rss_entry_id)
            )
            entry = entry_result.scalar_one_or_none()

            if not entry:
                result['error_message'] = "RSS entry not found"
                return result

            source_result = await session.execute(
                select(RSSSource).where(RSSSource.id == entry.source_id)
            )
            source = source_result.scalar_one_or_none()

            if not source:
                result['error_message'] = "RSS source not found"
                return result

        # Classify with LLM
        llm_result = await classifier.classify(article.extracted_text, entry.title)

        if not llm_result:
            result['error_message'] = "LLM classification failed"
            # Update status to failed
            async with async_session_maker() as session:
                entry_update = await session.execute(
                    select(RSSEntry).where(RSSEntry.id == entry.id)
                )
                entry_obj = entry_update.scalar_one_or_none()
                if entry_obj:
                    entry_obj.processing_status = 'classification_failed'
                    await session.commit()
            return result

        # Store classification
        classification_id = await store_classification(article, entry, source, llm_result)

        if classification_id:
            result['success'] = True
            result['classification_id'] = classification_id
            logger.info(f"Successfully classified article {article.id}")
        else:
            result['error_message'] = "Failed to store classification"

        return result

    except Exception as e:
        logger.error(f"Error classifying article {article.id}: {e}")
        result['error_message'] = str(e)
        return result


async def classify_pending_articles(batch_size: int = 20):
    """Classify all pending articles"""
    logger.info("Starting article classification job...")

    # Create processing log
    log_id = None
    async with async_session_maker() as session:
        log = ProcessingLog(
            job_type="llm_classification",
            status="running",
            metadata={"started_at": datetime.now(timezone.utc).isoformat()}
        )
        session.add(log)
        await session.commit()
        log_id = log.id

    total_processed = 0
    total_success = 0
    total_failed = 0

    # Initialize classifier
    classifier = LLMClassifier()

    # Fetch articles that are scraped but not yet classified
    async with async_session_maker() as session:
        # Get articles where rss_entry status is 'scraped' (not yet classified)
        result = await session.execute(
            select(Article)
            .join(RSSEntry, Article.rss_entry_id == RSSEntry.id)
            .where(RSSEntry.processing_status == 'scraped')
            .limit(batch_size)
        )
        articles = result.scalars().all()

        logger.info(f"Found {len(articles)} articles to classify")

        for article in articles:
            result = await classify_article(article, classifier)
            total_processed += 1

            if result['success']:
                total_success += 1
            else:
                total_failed += 1

            # Small delay between API calls
            await asyncio.sleep(1)

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
            log.metadata = {
                "classifications_created": total_success,
                "classifications_failed": total_failed,
            }
            await session.commit()

    logger.info(f"Classification completed: {total_success} success, {total_failed} failed out of {total_processed} total")


async def main():
    """Main entry point"""
    try:
        await classify_pending_articles(batch_size=20)
    except Exception as e:
        logger.error(f"Article classification job failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
