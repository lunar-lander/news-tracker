"""
Analytics API Endpoints
Uses TimescaleDB time_bucket() for efficient time-series aggregation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db

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


class BatchTimeseriesItem(BaseModel):
    """Timeseries data for a single tag in a batch request"""

    tag: str
    timeseries: List[TimeseriesDataPoint]
    total: int


class BatchTimeseriesResponse(BaseModel):
    """Batch timeseries response for multiple tags"""

    items: List[BatchTimeseriesItem]


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


def _validate_dates(start_date: str, end_date: str):
    """Parse and validate date strings"""
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        return start_dt, end_dt
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)."
        )


def _granularity_to_interval(granularity: str) -> str:
    """Convert granularity string to PostgreSQL interval"""
    mapping = {"day": "1 day", "week": "1 week", "month": "1 month"}
    if granularity not in mapping:
        raise HTTPException(
            status_code=400, detail="Invalid granularity. Use: day, week, month"
        )
    return mapping[granularity]


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
    Get time series data for news events using TimescaleDB time_bucket().
    """
    start_dt, end_dt = _validate_dates(start_date, end_date)
    interval = _granularity_to_interval(granularity)

    # Build parameterized SQL with time_bucket
    filters = ["published_at >= :start_dt", "published_at <= :end_dt"]
    params: Dict[str, Any] = {
        "start_dt": start_dt,
        "end_dt": end_dt,
    }

    if tag:
        filters.append(":tag = ANY(all_tags)")
        params["tag"] = tag
    elif tags:
        tag_list = [t.strip() for t in tags.split(",")]
        filters.append("all_tags && CAST(:tag_arr AS varchar[])")
        params["tag_arr"] = tag_list

    if state:
        filters.append("state = :state")
        params["state"] = state

    where_clause = " AND ".join(filters)

    # Main aggregation query using time_bucket
    sql = text(
        f"""
        SELECT
            time_bucket('{interval}', published_at) AS bucket,
            COUNT(*) AS count
        FROM news_events
        WHERE {where_clause}
        GROUP BY bucket
        ORDER BY bucket
    """
    )
    result = await db.execute(sql, params)
    rows = result.fetchall()

    timeseries_list = [
        {"timestamp": row.bucket, "count": row.count, "breakdown": {}} for row in rows
    ]

    # If group_by requested, run a second query for breakdown
    if group_by in ("tag", "state", "severity"):
        group_col = {"tag": "primary_tag", "state": "state", "severity": "severity"}[
            group_by
        ]
        breakdown_sql = text(
            f"""
            SELECT
                time_bucket('{interval}', published_at) AS bucket,
                {group_col} AS group_key,
                COUNT(*) AS count
            FROM news_events
            WHERE {where_clause} AND {group_col} IS NOT NULL
            GROUP BY bucket, group_key
            ORDER BY bucket
        """
        )
        bd_result = await db.execute(breakdown_sql, params)
        bd_rows = bd_result.fetchall()

        # Build lookup: bucket -> {key: count}
        breakdown_map: Dict[datetime, Dict[str, int]] = {}
        for row in bd_rows:
            breakdown_map.setdefault(row.bucket, {})[row.group_key] = row.count

        for item in timeseries_list:
            item["breakdown"] = breakdown_map.get(item["timestamp"], {})

    # Summary stats
    total_count = sum(item["count"] for item in timeseries_list)
    counts = [item["count"] for item in timeseries_list]
    average = sum(counts) / len(counts) if counts else 0
    peak_item = (
        max(timeseries_list, key=lambda x: x["count"]) if timeseries_list else None
    )

    summary = {
        "total": total_count,
        "average": round(average, 2),
        "peak": (
            {
                "count": peak_item["count"],
                "date": peak_item["timestamp"],
            }
            if peak_item
            else None
        ),
    }

    return TimeseriesResponse(
        timeseries=[TimeseriesDataPoint(**item) for item in timeseries_list],
        summary=summary,
    )


@router.get("/timeseries/batch", response_model=BatchTimeseriesResponse)
async def get_timeseries_batch(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    tags: str = Query(..., description="Comma-separated list of tags"),
    granularity: str = Query("day", description="Granularity: day, week, month"),
    state: Optional[str] = Query(None, description="Filter by state"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get time series data for multiple tags in a single query.
    Used by the dashboard to avoid N+1 API calls.
    """
    start_dt, end_dt = _validate_dates(start_date, end_date)
    interval = _granularity_to_interval(granularity)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    if not tag_list:
        raise HTTPException(status_code=400, detail="At least one tag required")

    filters = ["published_at >= :start_dt", "published_at <= :end_dt"]
    params: Dict[str, Any] = {
        "start_dt": start_dt,
        "end_dt": end_dt,
        "tag_arr": tag_list,
    }

    if state:
        filters.append("state = :state")
        params["state"] = state

    where_clause = " AND ".join(filters)

    # Single query: get per-tag timeseries using unnest
    sql = text(
        f"""
        SELECT
            tag,
            time_bucket('{interval}', published_at) AS bucket,
            COUNT(*) AS count
        FROM news_events, unnest(all_tags) AS tag
        WHERE {where_clause}
          AND tag = ANY(:tag_arr)
        GROUP BY tag, bucket
        ORDER BY tag, bucket
    """
    )

    result = await db.execute(sql, params)
    rows = result.fetchall()

    # Group results by tag
    tag_data: Dict[str, List[Dict]] = {t: [] for t in tag_list}
    tag_totals: Dict[str, int] = {t: 0 for t in tag_list}

    for row in rows:
        if row.tag in tag_data:
            tag_data[row.tag].append({"timestamp": row.bucket, "count": row.count})
            tag_totals[row.tag] += row.count

    items = [
        BatchTimeseriesItem(
            tag=t,
            timeseries=[
                TimeseriesDataPoint(timestamp=d["timestamp"], count=d["count"])
                for d in tag_data.get(t, [])
            ],
            total=tag_totals.get(t, 0),
        )
        for t in tag_list
    ]

    return BatchTimeseriesResponse(items=items)


@router.get("/geographic", response_model=GeographicResponse)
async def get_geographic(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    granularity: str = Query("state", description="Granularity: state or city"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get geographic distribution of news events using SQL aggregation.
    """
    start_dt, end_dt = _validate_dates(start_date, end_date)

    if granularity not in ("state", "city"):
        raise HTTPException(
            status_code=400, detail="Granularity must be 'state' or 'city'"
        )

    geo_col = "state" if granularity == "state" else "city"

    filters = [
        "published_at >= :start_dt",
        "published_at <= :end_dt",
        f"{geo_col} IS NOT NULL",
    ]
    params: Dict[str, Any] = {"start_dt": start_dt, "end_dt": end_dt}

    if tag:
        filters.append(":tag = ANY(all_tags)")
        params["tag"] = tag

    where_clause = " AND ".join(filters)

    # Main geographic aggregation
    sql = text(
        f"""
        SELECT
            {geo_col} AS geo_key,
            COUNT(*) AS count
        FROM news_events
        WHERE {where_clause}
        GROUP BY geo_key
        ORDER BY count DESC
    """
    )
    result = await db.execute(sql, params)
    rows = result.fetchall()

    # Get tag breakdown per geography
    breakdown_sql = text(
        f"""
        SELECT
            {geo_col} AS geo_key,
            primary_tag,
            COUNT(*) AS count
        FROM news_events
        WHERE {where_clause} AND primary_tag IS NOT NULL
        GROUP BY geo_key, primary_tag
        ORDER BY geo_key, count DESC
    """
    )
    bd_result = await db.execute(breakdown_sql, params)
    bd_rows = bd_result.fetchall()

    breakdown_map: Dict[str, Dict[str, int]] = {}
    for row in bd_rows:
        breakdown_map.setdefault(row.geo_key, {})[row.primary_tag] = row.count

    geographic = [
        GeographicDataPoint(
            state=row.geo_key,
            count=row.count,
            breakdown=breakdown_map.get(row.geo_key, {}),
        )
        for row in rows
    ]

    return GeographicResponse(geographic=geographic)


@router.get("/trending", response_model=TrendingResponse)
async def get_trending(
    timeframe: str = Query("24h", description="Timeframe: 24h, 7d, 30d"),
    limit: int = Query(10, description="Number of results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get trending tags (increasing in frequency) using SQL aggregation.
    Compares current period vs previous period of same length.
    """
    if timeframe == "24h":
        hours = 24
    elif timeframe == "7d":
        hours = 24 * 7
    elif timeframe == "30d":
        hours = 24 * 30
    else:
        raise HTTPException(
            status_code=400, detail="Invalid timeframe. Use: 24h, 7d, 30d"
        )

    now = datetime.now(timezone.utc)
    current_start = now - timedelta(hours=hours)
    previous_start = now - timedelta(hours=hours * 2)

    # Single query with conditional aggregation for both periods
    sql = text(
        """
        SELECT
            primary_tag AS tag,
            COUNT(*) FILTER (WHERE published_at >= :current_start) AS current_count,
            COUNT(*) FILTER (WHERE published_at >= :previous_start AND published_at < :current_start) AS previous_count
        FROM news_events
        WHERE published_at >= :previous_start
          AND primary_tag IS NOT NULL
        GROUP BY primary_tag
        HAVING COUNT(*) FILTER (WHERE published_at >= :current_start) > 0
        ORDER BY current_count DESC
        LIMIT :limit
    """
    )

    result = await db.execute(
        sql,
        {
            "current_start": current_start,
            "previous_start": previous_start,
            "limit": limit,
        },
    )
    rows = result.fetchall()

    trending_items = []
    for row in rows:
        current = row.current_count
        previous = row.previous_count

        if previous == 0:
            pct = 100.0 if current > 0 else 0.0
        else:
            pct = ((current - previous) / previous) * 100

        trend = "up" if pct > 10 else ("down" if pct < -10 else "stable")

        trending_items.append(
            TrendingItem(
                tag=row.tag,
                current_count=current,
                previous_count=previous,
                percentage_change=round(pct, 2),
                trend=trend,
            )
        )

    # Re-sort by percentage change
    trending_items.sort(key=lambda x: x.percentage_change, reverse=True)

    return TrendingResponse(trending=trending_items)
