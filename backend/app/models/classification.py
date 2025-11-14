"""
Classification model
"""

from sqlalchemy import Column, Integer, String, Text, Float, Date, TIMESTAMP, ForeignKey, JSON, ARRAY, DECIMAL
from sqlalchemy.sql import func
from app.database import Base


class Classification(Base):
    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    llm_provider = Column(String(50))
    llm_model = Column(String(100))
    classified_at = Column(TIMESTAMP, server_default=func.now())

    # Classifications
    tags = Column(ARRAY(String(100)))
    tag_confidences = Column(JSON)

    # Metadata
    summary = Column(Text)
    severity = Column(String(20))
    incident_date = Column(Date)
    state = Column(String(100))
    city = Column(String(100))
    district = Column(String(100))
    location_confidence = Column(Float)

    # Entities
    persons = Column(ARRAY(String(255)))
    organizations = Column(ARRAY(String(255)))

    # LLM response
    raw_llm_response = Column(JSON)
    llm_tokens_used = Column(Integer)
    llm_cost_usd = Column(DECIMAL(10, 6))

    created_at = Column(TIMESTAMP, server_default=func.now())
