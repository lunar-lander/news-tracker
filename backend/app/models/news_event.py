"""
News Event model (denormalized for fast queries)
"""

import datetime as dt
from typing import Optional

from sqlalchemy import ARRAY, TIMESTAMP, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class NewsEvent(Base):
    __tablename__ = "news_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rss_entry_id: Mapped[int] = mapped_column(
        ForeignKey("rss_entries.id", ondelete="CASCADE")
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE")
    )
    classification_id: Mapped[int] = mapped_column(
        ForeignKey("classifications.id", ondelete="CASCADE")
    )

    # Denormalized fields
    headline: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, default=None)
    source_name: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    source_url: Mapped[Optional[str]] = mapped_column(Text, default=None)
    published_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))
    incident_date: Mapped[Optional[dt.date]] = mapped_column(Date, default=None)

    # Categories
    primary_tag: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    all_tags: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(100)), default=None
    )
    severity: Mapped[Optional[str]] = mapped_column(String(20), default=None)

    # Location
    state: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    city: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    region: Mapped[Optional[str]] = mapped_column(String(100), default=None)

    created_at: Mapped[Optional[dt.datetime]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
