"""
Article model
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rss_entry_id: Mapped[int] = mapped_column(
        ForeignKey("rss_entries.id", ondelete="CASCADE")
    )
    full_text: Mapped[Optional[str]] = mapped_column(Text, default=None)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, default=None)
    word_count: Mapped[Optional[int]] = mapped_column(default=None)
    language: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    scraped_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )
    scraping_method: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    scraping_success: Mapped[Optional[bool]] = mapped_column(default=None)
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
