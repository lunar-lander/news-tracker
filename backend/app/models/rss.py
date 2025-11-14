"""
RSS Source and Entry models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class RSSSource(Base):
    __tablename__ = "rss_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False, unique=True)
    category = Column(String(100))
    language = Column(String(50))
    region = Column(String(100))
    priority = Column(String(20))
    refresh_interval = Column(Integer, default=300)
    enabled = Column(Boolean, default=True)
    last_fetched_at = Column(TIMESTAMP)
    last_success_at = Column(TIMESTAMP)
    consecutive_failures = Column(Integer, default=0)
    meta_data = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class RSSEntry(Base):
    __tablename__ = "rss_entries"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("rss_sources.id", ondelete="CASCADE"))
    guid = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    link = Column(Text, nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    author = Column(String(255))
    raw_data = Column(JSON)
    content_hash = Column(String(64))
    processing_status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
