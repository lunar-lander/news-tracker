"""
News Events API Endpoints
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.news_event import NewsEvent
from app.models.classification import Classification
from app.models.article import Article

router = APIRouter(prefix="/api/v1/events", tags=["events"])


class NewsEventResponse(BaseModel):
    """News event response model"""
    id: int
    headline: str
    summary: Optional[str]
    source_name: Optional[str]
    source_url: Optional[str]
    published_at: datetime
    incident_date: Optional[datetime]
    primary_tag: Optional[str]
    all_tags: List[str]
    severity: Optional[str]
    state: Optional[str]
    city: Optional[str]
    region: Optional[str]

    class Config:
        from_attributes = True


class EventDetailResponse(NewsEventResponse):
    """Detailed news event response with additional fields"""
    full_text: Optional[str] = None
    entities: Optional[dict] = None
    classification_confidence: Optional[float] = None
    llm_model: Optional[str] = None


class EventsListResponse(BaseModel):
    """List response with pagination"""
    data: List[NewsEventResponse]
    pagination: dict


@router.get("", response_model=EventsListResponse)
async def list_events(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    state: Optional[str] = Query(None, description="State name"),
    city: Optional[str] = Query(None, description="City name"),
    severity: Optional[str] = Query(None, description="Severity level"),
    limit: int = Query(100, le=1000, description="Number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    sort: str = Query("published_at", description="Sort field"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List news events with filtering and pagination
    """
    # Build query
    query = select(NewsEvent)

    # Apply filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.where(NewsEvent.published_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.where(NewsEvent.published_at <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        # Filter events that have any of the specified tags
        query = query.where(NewsEvent.all_tags.overlap(tag_list))

    if state:
        query = query.where(NewsEvent.state == state)

    if city:
        query = query.where(NewsEvent.city == city)

    if severity:
        query = query.where(NewsEvent.severity == severity)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply sorting
    if sort == "published_at":
        order_by = NewsEvent.published_at.desc() if order == "desc" else NewsEvent.published_at.asc()
    elif sort == "incident_date":
        order_by = NewsEvent.incident_date.desc() if order == "desc" else NewsEvent.incident_date.asc()
    else:
        order_by = NewsEvent.published_at.desc()

    query = query.order_by(order_by).limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    return EventsListResponse(
        data=[NewsEventResponse.model_validate(event) for event in events],
        pagination={
            "total": total,
            "limit": limit,
            "offset": offset,
            "hasMore": offset + limit < total,
        }
    )


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event_detail(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a single news event
    """
    # Get event with related data
    query = (
        select(NewsEvent)
        .where(NewsEvent.id == event_id)
    )
    result = await db.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get related article and classification
    if event.article_id:
        article_query = select(Article).where(Article.id == event.article_id)
        article_result = await db.execute(article_query)
        article = article_result.scalar_one_or_none()
    else:
        article = None

    if event.classification_id:
        classification_query = select(Classification).where(Classification.id == event.classification_id)
        classification_result = await db.execute(classification_query)
        classification = classification_result.scalar_one_or_none()
    else:
        classification = None

    # Build detailed response
    response_data = NewsEventResponse.model_validate(event).model_dump()

    # Add additional details
    if article:
        response_data["full_text"] = article.extracted_text

    if classification:
        response_data["entities"] = {
            "persons": classification.persons,
            "organizations": classification.organizations,
        }
        # Calculate average confidence
        if classification.tag_confidences:
            confidences = list(classification.tag_confidences.values())
            response_data["classification_confidence"] = sum(confidences) / len(confidences) if confidences else None
        response_data["llm_model"] = classification.llm_model

    return EventDetailResponse(**response_data)
