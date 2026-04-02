"""
Classification model
"""

import datetime as dt
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import ARRAY, DECIMAL, TIMESTAMP, Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.database import Base


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE")
    )
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    llm_model: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    classified_at: Mapped[Optional[dt.datetime]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    # Classifications
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(100)), default=None)
    tag_confidences: Mapped[Optional[Any]] = mapped_column(JSON, default=None)

    # Metadata
    summary: Mapped[Optional[str]] = mapped_column(Text, default=None)
    severity: Mapped[Optional[str]] = mapped_column(String(20), default=None)
    incident_date: Mapped[Optional[dt.date]] = mapped_column(Date, default=None)
    state: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    city: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    district: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    location_confidence: Mapped[Optional[float]] = mapped_column(Float, default=None)

    # Entities
    persons: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(255)), default=None
    )
    organizations: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(255)), default=None
    )

    # LLM response
    raw_llm_response: Mapped[Optional[Any]] = mapped_column(JSON, default=None)
    llm_tokens_used: Mapped[Optional[int]] = mapped_column(default=None)
    llm_cost_usd: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 6), default=None
    )

    created_at: Mapped[Optional[dt.datetime]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
