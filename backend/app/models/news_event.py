"""
News Event model (denormalized for fast queries)
"""

from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.sql import func
from app.database import Base


class NewsEvent(Base):
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True, index=True)
    rss_entry_id = Column(Integer, ForeignKey("rss_entries.id", ondelete="CASCADE"))
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    classification_id = Column(Integer, ForeignKey("classifications.id", ondelete="CASCADE"))

    # Denormalized fields
    headline = Column(Text, nullable=False)
    summary = Column(Text)
    source_name = Column(String(255))
    source_url = Column(Text)
    published_at = Column(TIMESTAMP, nullable=False)
    incident_date = Column(Date)

    # Categories
    primary_tag = Column(String(100))
    all_tags = Column(ARRAY(String(100)))
    severity = Column(String(20))

    # Location
    state = Column(String(100))
    city = Column(String(100))
    region = Column(String(100))

    created_at = Column(TIMESTAMP, server_default=func.now())
