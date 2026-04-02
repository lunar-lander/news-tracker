"""
RSS Source and Entry models
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.database import Base


class RSSSource(Base):
    __tablename__ = "rss_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text, unique=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    language: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    region: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    priority: Mapped[Optional[str]] = mapped_column(String(20), default=None)
    refresh_interval: Mapped[int] = mapped_column(default=300)
    enabled: Mapped[bool] = mapped_column(default=True)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )
    last_success_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )
    consecutive_failures: Mapped[int] = mapped_column(default=0)
    meta_data: Mapped[Optional[Any]] = mapped_column(JSON, default=None)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RSSEntry(Base):
    __tablename__ = "rss_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("rss_sources.id", ondelete="CASCADE")
    )
    guid: Mapped[str] = mapped_column(Text, unique=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    link: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    author: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    raw_data: Mapped[Optional[Any]] = mapped_column(JSON, default=None)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
