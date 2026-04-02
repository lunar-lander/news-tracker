"""
Search API Endpoints
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db

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
    Search news events by headline using PostgreSQL full-text search.
    Uses the GIN tsvector index on news_events.headline for performance.
    """
    # Build parameterized query with full-text search
    filters = ["to_tsvector('english', headline) @@ plainto_tsquery('english', :query)"]
    params = {"query": q, "limit": limit, "offset": offset}

    if start_date:
        try:
            datetime.fromisoformat(start_date)
            filters.append("published_at >= :start_dt")
            params["start_dt"] = start_date
        except ValueError:
            pass

    if end_date:
        try:
            datetime.fromisoformat(end_date)
            filters.append("published_at <= :end_dt")
            params["end_dt"] = end_date
        except ValueError:
            pass

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        filters.append("all_tags && :tag_arr::varchar[]")
        params["tag_arr"] = tag_list

    if state:
        filters.append("state = :state")
        params["state"] = state

    where_clause = " AND ".join(filters)

    # Count total
    count_sql = text(f"SELECT COUNT(*) FROM news_events WHERE {where_clause}")
    total_result = await db.execute(count_sql, params)
    total = total_result.scalar()

    # Fetch results sorted by relevance then recency
    sql = text(
        f"""
        SELECT id, headline, summary, published_at, all_tags, state
        FROM news_events
        WHERE {where_clause}
        ORDER BY ts_rank(to_tsvector('english', headline), plainto_tsquery('english', :query)) DESC,
                 published_at DESC
        LIMIT :limit OFFSET :offset
    """
    )

    result = await db.execute(sql, params)
    rows = result.fetchall()

    results = [
        SearchResultItem(
            id=row.id,
            headline=row.headline,
            summary=row.summary,
            published_at=row.published_at,
            all_tags=row.all_tags or [],
            state=row.state,
        )
        for row in rows
    ]

    return SearchResponse(results=results, total=total)
