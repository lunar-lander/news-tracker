"""
Configuration API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.config import load_tags_config
from app.models.rss import RSSSource

router = APIRouter(prefix="/api/v1/config", tags=["config"])


class TagResponse(BaseModel):
    """Tag configuration response"""
    id: str
    label: str
    category: str
    color: str
    enabled: bool


class SourceResponse(BaseModel):
    """RSS source response"""
    id: int
    name: str
    category: Optional[str]
    language: Optional[str]
    enabled: bool
    last_fetched: Optional[datetime]
    health: str

    class Config:
        from_attributes = True


@router.get("/tags")
async def get_tags_config():
    """
    Get available tags configuration
    """
    tags_config = load_tags_config()
    enabled_categories = tags_config.get("enabled_categories", [])
    category_definitions = tags_config.get("category_definitions", {})

    tags = []
    for tag_id in enabled_categories:
        if tag_id in category_definitions:
            definition = category_definitions[tag_id]
            tags.append(
                TagResponse(
                    id=tag_id,
                    label=definition.get("label", tag_id.replace("_", " ").title()),
                    category=definition.get("category", "general"),
                    color=definition.get("color", "#888888"),
                    enabled=True,
                )
            )

    return {"tags": tags}


@router.get("/sources")
async def get_sources_config(
    db: AsyncSession = Depends(get_db),
):
    """
    Get RSS sources configuration and health status
    """
    query = select(RSSSource)
    result = await db.execute(query)
    sources = result.scalars().all()

    source_responses = []
    for source in sources:
        # Determine health status
        if not source.enabled:
            health = "disabled"
        elif source.consecutive_failures >= 3:
            health = "unhealthy"
        elif source.last_success_at:
            health = "healthy"
        else:
            health = "unknown"

        source_responses.append(
            {
                "id": source.id,
                "name": source.name,
                "category": source.category,
                "language": source.language,
                "enabled": source.enabled,
                "lastFetched": source.last_fetched_at,
                "health": health,
            }
        )

    return {"sources": source_responses}
