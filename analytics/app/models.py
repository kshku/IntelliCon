from datetime import datetime

from sqlalchemy import Column, Float, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


class JobExecutionLog(Base):
    __tablename__ = "job_execution_log"
    __table_args__ = (
        Index("idx_job_execution_log_name", "job_name"),
        Index("idx_job_execution_log_started", "started_at"),
        {"schema": "analytics"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="running")
    started_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    completed_at = Column(TIMESTAMP, nullable=True)
    rows_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)


class HotspotResult(Base):
    __tablename__ = "hotspot_results"
    __table_args__ = {"schema": "analytics"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    crime_count = Column(Integer, nullable=True)
    dominant_crime_type = Column(String(100), nullable=True)
    radius_meters = Column(Float, nullable=True)
    computed_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)


class TrendResult(Base):
    __tablename__ = "trend_results"
    __table_args__ = {"schema": "analytics"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    crime_head_id = Column(Integer, nullable=True)
    crime_head_name = Column(String(100), nullable=True)
    period = Column(String(20), nullable=True)
    period_type = Column(String(10), nullable=True)
    case_count = Column(Integer, nullable=True)
    yoy_change_pct = Column(Float, nullable=True)
    computed_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)


class PredictionResult(Base):
    __tablename__ = "prediction_results"
    __table_args__ = {"schema": "analytics"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, nullable=True)
    district_name = Column(String(100), nullable=True)
    crime_head_id = Column(Integer, nullable=True)
    crime_head_name = Column(String(100), nullable=True)
    predicted_count = Column(Float, nullable=True)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    prediction_period = Column(String(20), nullable=True)
    computed_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
