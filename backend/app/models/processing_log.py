"""
Processing Log model
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import TIMESTAMP, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.database import Base


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_type: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )
    status: Mapped[Optional[str]] = mapped_column(String(20), default=None)
    items_processed: Mapped[int] = mapped_column(default=0)
    items_failed: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)
    meta_data: Mapped[Optional[Any]] = mapped_column(JSON, default=None)
