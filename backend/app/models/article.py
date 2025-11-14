"""
Article model
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    rss_entry_id = Column(Integer, ForeignKey("rss_entries.id", ondelete="CASCADE"))
    full_text = Column(Text)
    extracted_text = Column(Text)
    word_count = Column(Integer)
    language = Column(String(50))
    scraped_at = Column(TIMESTAMP)
    scraping_method = Column(String(100))
    scraping_success = Column(Boolean)
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
