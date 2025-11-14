"""
Search API Endpoints
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.news_event import NewsEvent

router = APIRouter(prefix="/api/v1/search", tags=["search"])


class SearchResultItem(BaseModel):
    """Search result item"""
    id: int
    headline: str
    summary: Optional[str]
    published_at: datetime
    all_tags: List[str]
    state: Optional[str]

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response"""
    results: List[SearchResultItem]
    total: int


@router.get("", response_model=SearchResponse)
async def search_events(
    q: str = Query(..., description="Search query (searches headlines)"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    limit: int = Query(100, le=1000, description="Number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search news events by headline
    """
    # Build base query with text search
    query = select(NewsEvent).where(
        NewsEvent.headline.ilike(f"%{q}%")
    )

    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.where(NewsEvent.published_at >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.where(NewsEvent.published_at <= end_dt)
        except ValueError:
            pass

    # Apply tag filter
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.where(NewsEvent.all_tags.overlap(tag_list))

    # Apply state filter
    if state:
        query = query.where(NewsEvent.state == state)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and sort by relevance (most recent first)
    query = query.order_by(NewsEvent.published_at.desc()).limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    return SearchResponse(
        results=[SearchResultItem.model_validate(event) for event in events],
        total=total
    )
