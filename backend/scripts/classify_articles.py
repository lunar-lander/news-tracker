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

from app.config import get_config_path, load_llm_config, load_tags_config, settings
from app.database import async_session_maker
from app.models.article import Article
from app.models.rss import RSSEntry, RSSSource
from app.models.classification import Classification
from app.models.news_event import NewsEvent
from app.models.processing_log import ProcessingLog

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        prompt_path = get_config_path() / "prompts" / "classification.txt"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load classification prompt: {e}")
            raise

    def _get_enabled_tags(self) -> List[str]:
        """Get list of enabled tags"""
        enabled = self.tags_config.get("enabled_categories", [])
        return enabled

    def _build_prompt(self, article_text: str, headline: str) -> str:
        """Build classification prompt with article text"""
        enabled_tags = self._get_enabled_tags()
        tags_list = ", ".join(enabled_tags)

        prompt = self.classification_prompt.replace("{article_text}", article_text)
        prompt = prompt.replace("{available_tags}", tags_list)

        return prompt

    @staticmethod
    def _clean_json(text: str) -> Optional[Dict[str, Any]]:
        """Try hard to extract valid JSON from LLM response text."""
        # Strip markdown code fences
        text = re.sub(r"```(?:json)?\s*", "", text).strip()

        # Find JSON object
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            return None

        raw = json_match.group()

        # First attempt: parse directly
        try:
            return json.loads(raw)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            pass

        # Fix common LLM JSON errors: trailing commas before } or ]
        cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
        try:
            return json.loads(cleaned)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            pass

        # Fix unescaped quotes inside string values
        try:
            # More aggressive: replace single quotes with double
            cleaned2 = raw.replace("'", '"')
            cleaned2 = re.sub(r",\s*([}\]])", r"\1", cleaned2)
            return json.loads(cleaned2)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return None

    async def classify_with_gemini(
        self, prompt: str, provider_cfg: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Classify using Google Gemini (google.genai SDK)"""
        try:
            from google import genai  # type: ignore[import-not-found]
            from google.genai import types  # type: ignore[import-not-found]

            cfg = provider_cfg or self.llm_config.get("primary") or {}
            api_key = cfg.get("api_key") or settings.google_api_key
            if not api_key:
                logger.error("GOOGLE_API_KEY not set")
                return None

            client: Any = genai.Client(api_key=api_key)

            model_name = cfg.get("model", "gemini-2.5-flash-lite")
            logger.info(f"Calling Gemini API with model {model_name}")

            response: Any = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=cfg.get("temperature", 0.2),
                    max_output_tokens=cfg.get("max_tokens", 2048),
                    response_mime_type="application/json",
                ),
            )

            # Extract text from response
            response_text: str = response.text

            # Try to parse JSON from response
            result = self._clean_json(response_text)
            if result:
                result["_raw_response"] = response_text
                result["_tokens_used"] = (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata") and response.usage_metadata
                    else 0
                )
                return result
            else:
                logger.error(
                    "Could not find valid JSON in Gemini response: %s",
                    response_text[:200],
                )
                return None

        except Exception as e:
            logger.error(f"Gemini classification failed: {e}")
            return None

    async def classify_with_claude(
        self, prompt: str, provider_cfg: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Classify using Anthropic Claude"""
        try:
            from anthropic import AsyncAnthropic  # type: ignore[import-not-found]

            cfg = provider_cfg or self.llm_config.get("fallback") or {}
            api_key = cfg.get("api_key") or settings.anthropic_api_key
            if not api_key:
                logger.error("ANTHROPIC_API_KEY not set")
                return None

            client: Any = AsyncAnthropic(api_key=api_key)  # type: ignore[reportUnknownVariableType]

            model = cfg.get("model", "claude-haiku-4-20250414")
            logger.info(f"Calling Claude API with model {model}")

            message: Any = await client.messages.create(
                model=model,
                max_tokens=cfg.get("max_tokens", 2048),
                temperature=cfg.get("temperature", 0.2),
                messages=[{"role": "user", "content": prompt}],
            )

            response_text: str = message.content[0].text

            # Try to parse JSON
            result = self._clean_json(response_text)
            if result:
                result["_raw_response"] = response_text
                result["_tokens_used"] = (
                    message.usage.input_tokens + message.usage.output_tokens
                )
                return result
            else:
                logger.error("Could not find valid JSON in Claude response")
                return None

        except Exception as e:
            logger.error(f"Claude classification failed: {e}")
            return None

    async def classify_with_openai(
        self, prompt: str, provider_cfg: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Classify using OpenAI"""
        try:
            from openai import AsyncOpenAI  # type: ignore[import-not-found]

            cfg = provider_cfg or self.llm_config.get("openai") or {}
            api_key = cfg.get("api_key") or settings.openai_api_key
            if not api_key:
                logger.error("OPENAI_API_KEY not set")
                return None

            client: Any = AsyncOpenAI(api_key=api_key)  # type: ignore[reportUnknownVariableType]

            model = cfg.get("model", "gpt-4.1-mini")
            logger.info(f"Calling OpenAI API with model {model}")

            response: Any = await client.chat.completions.create(
                model=model,
                max_tokens=cfg.get("max_tokens", 2048),
                temperature=cfg.get("temperature", 0.2),
                messages=[{"role": "user", "content": prompt}],
            )

            response_text: str = response.choices[0].message.content or ""

            result = self._clean_json(response_text)
            if result:
                result["_raw_response"] = response_text
                result["_tokens_used"] = (
                    response.usage.total_tokens if response.usage else 0
                )
                return result
            else:
                logger.error("Could not find valid JSON in OpenAI response")
                return None

        except Exception as e:
            logger.error(f"OpenAI classification failed: {e}")
            return None

    def _get_classify_fn(self, provider: str):
        """Return the classify coroutine for the given provider name."""
        dispatch = {
            "google": self.classify_with_gemini,
            "gemini": self.classify_with_gemini,
            "anthropic": self.classify_with_claude,
            "openai": self.classify_with_openai,
        }
        return dispatch.get(provider)

    async def classify(
        self, article_text: str, headline: str
    ) -> Optional[Dict[str, Any]]:
        """Classify article using dynamically resolved primary/fallback providers."""
        prompt = self._build_prompt(article_text, headline)

        # Try primary provider
        primary_cfg = self.llm_config.get("primary", {})
        primary_provider = primary_cfg.get("provider", "google")
        classify_fn = self._get_classify_fn(primary_provider)

        if classify_fn:
            result = await classify_fn(prompt, primary_cfg)
            if result:
                result["_provider"] = primary_provider
                result["_model"] = primary_cfg.get("model", "unknown")
                return result

        # Try fallback provider
        fallback_cfg = self.llm_config.get("fallback")
        if fallback_cfg:
            fallback_provider = fallback_cfg.get("provider", "anthropic")
            logger.warning(
                f"Primary LLM ({primary_provider}) failed, trying fallback ({fallback_provider})"
            )
            classify_fn = self._get_classify_fn(fallback_provider)
            if classify_fn:
                result = await classify_fn(prompt, fallback_cfg)
                if result:
                    result["_provider"] = fallback_provider
                    result["_model"] = fallback_cfg.get("model", "unknown")
                    return result

        logger.error("All LLM providers failed")
        return None


# Canonical Indian state/UT names for normalisation
_VALID_STATES = {
    "andhra pradesh",
    "arunachal pradesh",
    "assam",
    "bihar",
    "chhattisgarh",
    "goa",
    "gujarat",
    "haryana",
    "himachal pradesh",
    "jharkhand",
    "karnataka",
    "kerala",
    "madhya pradesh",
    "maharashtra",
    "manipur",
    "meghalaya",
    "mizoram",
    "nagaland",
    "odisha",
    "punjab",
    "rajasthan",
    "sikkim",
    "tamil nadu",
    "telangana",
    "tripura",
    "uttar pradesh",
    "uttarakhand",
    "west bengal",
    "delhi",
    "jammu and kashmir",
    "ladakh",
    "chandigarh",
    "puducherry",
    "andaman and nicobar islands",
    "dadra and nagar haveli",
    "daman and diu",
    "lakshadweep",
}

# Build a fast lookup: lowercase → title-cased canonical name
_STATE_LOOKUP: Dict[str, str] = {}
for _s in _VALID_STATES:
    canonical = _s.title()
    _STATE_LOOKUP[_s] = canonical
    # Also handle "state_xxx" prefixes: "state_uttar_pradesh" -> "uttar pradesh"
    _STATE_LOOKUP["state_" + _s.replace(" ", "_")] = canonical


def _normalize_state(raw: Optional[str]) -> Optional[str]:
    """Normalise an LLM-returned state value.

    Handles:
      - "state_delhi" → "Delhi"
      - "Delhi, Karnataka, Telangana" → "Delhi" (first valid one)
      - "kerala" → "Kerala"
      - None / empty → None
    """
    if not raw or not raw.strip():
        return None

    raw = raw.strip()

    # Direct hit (case-insensitive)
    if raw.lower() in _STATE_LOOKUP:
        return _STATE_LOOKUP[raw.lower()]

    # Multi-value: split by comma, pick the first valid state
    if "," in raw:
        for part in raw.split(","):
            part = part.strip().lower()
            if part in _STATE_LOOKUP:
                return _STATE_LOOKUP[part]

    # "state_xxx" pattern not yet in lookup (shouldn't happen but be safe)
    if raw.lower().startswith("state_"):
        cleaned = raw[6:].replace("_", " ").strip().lower()
        if cleaned in _STATE_LOOKUP:
            return _STATE_LOOKUP[cleaned]

    logger.warning("Unrecognised state value from LLM: %s", raw)
    return raw.title()  # Best-effort title-case


async def store_classification(
    article: Article, entry: RSSEntry, source: RSSSource, llm_result: Dict[str, Any]
) -> Optional[int]:
    """Store classification and create news event"""
    try:
        async with async_session_maker() as session:
            # Extract data from LLM result
            tags = llm_result.get("tags", [])
            tag_confidences = llm_result.get("tag_confidences", {})
            summary = llm_result.get("summary", "")
            severity = llm_result.get("severity", "medium")
            incident_date_str = llm_result.get("incident_date")
            state = _normalize_state(llm_result.get("state"))
            city = llm_result.get("city")
            district = llm_result.get("district")
            location_confidence = llm_result.get("location_confidence", 0.0)
            persons = llm_result.get("persons", [])
            organizations = llm_result.get("organizations", [])

            # Parse incident date
            incident_date = None
            if incident_date_str:
                try:
                    incident_date = datetime.fromisoformat(incident_date_str).date()
                except:
                    pass

            # Calculate LLM cost (rough estimate)
            tokens_used = llm_result.get("_tokens_used", 0)
            cost_per_million = (
                0.075 if llm_result.get("_provider") == "google" else 0.25
            )
            cost_usd = (tokens_used / 1_000_000) * cost_per_million

            # Create classification record
            classification = Classification(
                article_id=article.id,
                llm_provider=llm_result.get("_provider"),
                llm_model=llm_result.get("_model"),
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

            # Re-fetch entry within this session to avoid detached object issue
            entry_result = await session.execute(
                select(RSSEntry).where(RSSEntry.id == entry.id)
            )
            entry_obj = entry_result.scalar_one_or_none()
            if entry_obj:
                entry_obj.processing_status = "completed"

            await session.commit()

            logger.info(
                f"Stored classification {classification.id} for article {article.id}"
            )
            return classification.id

    except Exception as e:
        logger.error(f"Failed to store classification: {e}")
        return None


async def classify_article(
    article: Article, classifier: LLMClassifier
) -> Dict[str, Any]:
    """Classify a single article"""
    result: Dict[str, Any] = {
        "article_id": article.id,
        "success": False,
        "error_message": None,
    }

    try:
        # Get RSS entry and source
        async with async_session_maker() as session:
            entry_result = await session.execute(
                select(RSSEntry).where(RSSEntry.id == article.rss_entry_id)
            )
            entry = entry_result.scalar_one_or_none()

            if not entry:
                result["error_message"] = "RSS entry not found"
                return result

            source_result = await session.execute(
                select(RSSSource).where(RSSSource.id == entry.source_id)
            )
            source = source_result.scalar_one_or_none()

            if not source:
                result["error_message"] = "RSS source not found"
                return result

        # Build article text from headline + description to minimise token usage.
        # Fall back to full extracted text only when description is too brief.
        description = (entry.description or "").strip()
        if len(description) >= 50:
            article_text = f"Headline: {entry.title}\n\nDescription: {description}"
        else:
            article_text = article.extracted_text or f"Headline: {entry.title}"

        llm_result = await classifier.classify(article_text, entry.title)

        if not llm_result:
            result["error_message"] = "LLM classification failed"
            # Update status to failed
            async with async_session_maker() as session:
                entry_update = await session.execute(
                    select(RSSEntry).where(RSSEntry.id == entry.id)
                )
                entry_obj = entry_update.scalar_one_or_none()
                if entry_obj:
                    entry_obj.processing_status = "classification_failed"
                    await session.commit()
            return result

        # Store classification
        classification_id = await store_classification(
            article, entry, source, llm_result
        )

        if classification_id:
            result["success"] = True
            result["classification_id"] = classification_id
            logger.info(f"Successfully classified article {article.id}")
        else:
            result["error_message"] = "Failed to store classification"

        return result

    except Exception as e:
        logger.error(f"Error classifying article {article.id}: {e}")
        result["error_message"] = str(e)
        return result


async def classify_pending_articles(batch_size: int = 20):
    """Classify all pending articles.

    Returns quickly if there is nothing to classify so it can be polled
    at a high frequency without wasting resources.
    """
    # Quick-check: any work to do?
    async with async_session_maker() as session:
        result = await session.execute(
            select(Article.id)
            .join(RSSEntry, Article.rss_entry_id == RSSEntry.id)
            .where(RSSEntry.processing_status == "scraped")
            .limit(1)
        )
        if not result.scalar_one_or_none():
            return  # nothing to classify — exit silently

    logger.info("Starting article classification job...")

    # Create processing log
    log_id = None
    async with async_session_maker() as session:
        log = ProcessingLog(
            job_type="llm_classification",
            status="running",
            meta_data={"started_at": datetime.now(timezone.utc).isoformat()},
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
            .where(RSSEntry.processing_status == "scraped")
            .limit(batch_size)
        )
        articles = result.scalars().all()

        logger.info(f"Found {len(articles)} articles to classify")

        for article in articles:
            result = await classify_article(article, classifier)
            total_processed += 1

            if result["success"]:
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
            log.meta_data = {
                "classifications_created": total_success,
                "classifications_failed": total_failed,
            }
            await session.commit()

    logger.info(
        f"Classification completed: {total_success} success, {total_failed} failed out of {total_processed} total"
    )


async def main():
    """Main entry point"""
    try:
        await classify_pending_articles(batch_size=20)
    except Exception as e:
        logger.error(f"Article classification job failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
