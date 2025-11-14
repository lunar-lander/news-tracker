"""
Analytics API Endpoints
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.news_event import NewsEvent

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class TimeseriesDataPoint(BaseModel):
    """Single data point in time series"""
    timestamp: datetime
    count: int
    breakdown: Optional[dict] = None


class TimeseriesResponse(BaseModel):
    """Time series response"""
    timeseries: List[TimeseriesDataPoint]
    summary: dict


class GeographicDataPoint(BaseModel):
    """Geographic distribution data point"""
    state: str
    count: int
    breakdown: Optional[dict] = None


class GeographicResponse(BaseModel):
    """Geographic response"""
    geographic: List[GeographicDataPoint]


class TrendingItem(BaseModel):
    """Trending tag item"""
    tag: str
    current_count: int
    previous_count: int
    percentage_change: float
    trend: str


class TrendingResponse(BaseModel):
    """Trending response"""
    trending: List[TrendingItem]


@router.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    granularity: str = Query("day", description="Granularity: day, week, month"),
    tag: Optional[str] = Query(None, description="Specific tag to filter"),
    tags: Optional[str] = Query(None, description="Multiple tags (comma-separated)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    group_by: Optional[str] = Query(None, description="Group by: tag, state, severity"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get time series data for news events
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    # Determine time bucket based on granularity
    if granularity == "day":
        bucket_hours = 24
    elif granularity == "week":
        bucket_hours = 24 * 7
    elif granularity == "month":
        bucket_hours = 24 * 30
    else:
        raise HTTPException(status_code=400, detail="Invalid granularity")

    # Build base query
    query = select(NewsEvent).where(
        and_(
            NewsEvent.published_at >= start_dt,
            NewsEvent.published_at <= end_dt,
        )
    )

    # Apply filters
    if tag:
        query = query.where(NewsEvent.all_tags.contains([tag]))
    elif tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.where(NewsEvent.all_tags.overlap(tag_list))

    if state:
        query = query.where(NewsEvent.state == state)

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    # Group events by time bucket
    timeseries_data = {}
    total_count = 0

    for event in events:
        # Calculate bucket timestamp
        if granularity == "day":
            bucket = event.published_at.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == "week":
            days_since_monday = event.published_at.weekday()
            bucket = (event.published_at - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # month
            bucket = event.published_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        bucket_str = bucket.isoformat()

        if bucket_str not in timeseries_data:
            timeseries_data[bucket_str] = {
                "timestamp": bucket,
                "count": 0,
                "breakdown": {}
            }

        timeseries_data[bucket_str]["count"] += 1
        total_count += 1

        # Add to breakdown if group_by specified
        if group_by == "tag" and event.primary_tag:
            tag_key = event.primary_tag
            timeseries_data[bucket_str]["breakdown"][tag_key] = \
                timeseries_data[bucket_str]["breakdown"].get(tag_key, 0) + 1
        elif group_by == "state" and event.state:
            state_key = event.state
            timeseries_data[bucket_str]["breakdown"][state_key] = \
                timeseries_data[bucket_str]["breakdown"].get(state_key, 0) + 1
        elif group_by == "severity" and event.severity:
            severity_key = event.severity
            timeseries_data[bucket_str]["breakdown"][severity_key] = \
                timeseries_data[bucket_str]["breakdown"].get(severity_key, 0) + 1

    # Convert to list and sort by timestamp
    timeseries_list = sorted(timeseries_data.values(), key=lambda x: x["timestamp"])

    # Calculate summary stats
    counts = [item["count"] for item in timeseries_list]
    average = sum(counts) / len(counts) if counts else 0

    peak_item = max(timeseries_list, key=lambda x: x["count"]) if timeseries_list else None

    summary = {
        "total": total_count,
        "average": round(average, 2),
        "peak": {
            "count": peak_item["count"],
            "date": peak_item["timestamp"],
        } if peak_item else None
    }

    return TimeseriesResponse(
        timeseries=[TimeseriesDataPoint(**item) for item in timeseries_list],
        summary=summary
    )


@router.get("/geographic", response_model=GeographicResponse)
async def get_geographic(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    granularity: str = Query("state", description="Granularity: state or city"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get geographic distribution of news events
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    # Build query
    query = select(NewsEvent).where(
        and_(
            NewsEvent.published_at >= start_dt,
            NewsEvent.published_at <= end_dt,
        )
    )

    if tag:
        query = query.where(NewsEvent.all_tags.contains([tag]))

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    # Group by geography
    geo_data = {}

    for event in events:
        if granularity == "state":
            geo_key = event.state if event.state else "Unknown"
        else:  # city
            geo_key = event.city if event.city else "Unknown"

        if geo_key not in geo_data:
            geo_data[geo_key] = {
                "state" if granularity == "state" else "city": geo_key,
                "count": 0,
                "breakdown": {}
            }

        geo_data[geo_key]["count"] += 1

        # Add tag breakdown
        if event.primary_tag:
            tag_key = event.primary_tag
            geo_data[geo_key]["breakdown"][tag_key] = \
                geo_data[geo_key]["breakdown"].get(tag_key, 0) + 1

    # Convert to list and sort by count
    geo_list = sorted(geo_data.values(), key=lambda x: x["count"], reverse=True)

    return GeographicResponse(
        geographic=[GeographicDataPoint(**item) for item in geo_list]
    )


@router.get("/trending", response_model=TrendingResponse)
async def get_trending(
    timeframe: str = Query("24h", description="Timeframe: 24h, 7d, 30d"),
    limit: int = Query(10, description="Number of results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get trending tags (increasing in frequency)
    """
    # Parse timeframe
    if timeframe == "24h":
        hours = 24
    elif timeframe == "7d":
        hours = 24 * 7
    elif timeframe == "30d":
        hours = 24 * 30
    else:
        raise HTTPException(status_code=400, detail="Invalid timeframe")

    now = datetime.utcnow()
    current_start = now - timedelta(hours=hours)
    previous_start = now - timedelta(hours=hours * 2)
    previous_end = current_start

    # Get current period events
    current_query = select(NewsEvent).where(
        NewsEvent.published_at >= current_start
    )
    current_result = await db.execute(current_query)
    current_events = current_result.scalars().all()

    # Get previous period events
    previous_query = select(NewsEvent).where(
        and_(
            NewsEvent.published_at >= previous_start,
            NewsEvent.published_at < previous_end,
        )
    )
    previous_result = await db.execute(previous_query)
    previous_events = previous_result.scalars().all()

    # Count tags in each period
    current_tags = {}
    for event in current_events:
        if event.primary_tag:
            current_tags[event.primary_tag] = current_tags.get(event.primary_tag, 0) + 1

    previous_tags = {}
    for event in previous_events:
        if event.primary_tag:
            previous_tags[event.primary_tag] = previous_tags.get(event.primary_tag, 0) + 1

    # Calculate trends
    trending_items = []
    for tag, current_count in current_tags.items():
        previous_count = previous_tags.get(tag, 0)

        # Calculate percentage change
        if previous_count == 0:
            percentage_change = 100.0 if current_count > 0 else 0.0
        else:
            percentage_change = ((current_count - previous_count) / previous_count) * 100

        # Determine trend direction
        if percentage_change > 10:
            trend = "up"
        elif percentage_change < -10:
            trend = "down"
        else:
            trend = "stable"

        trending_items.append(
            TrendingItem(
                tag=tag,
                current_count=current_count,
                previous_count=previous_count,
                percentage_change=round(percentage_change, 2),
                trend=trend,
            )
        )

    # Sort by percentage change (descending) and limit
    trending_items.sort(key=lambda x: x.percentage_change, reverse=True)
    trending_items = trending_items[:limit]

    return TrendingResponse(trending=trending_items)
