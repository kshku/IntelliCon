from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Float, Index, Integer, String, Text
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


class AnalyticsPrediction(Base):
    __tablename__ = "analytics_predictions"
    __table_args__ = (
        Index("idx_analytics_predictions_type", "prediction_type"),
        Index("idx_analytics_predictions_entity", "entity_type", "entity_id"),
        Index("idx_analytics_predictions_period", "period_date"),
        {"schema": "analytics"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    prediction_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    period_date = Column(TIMESTAMP, nullable=True)
    model_version = Column(String(50), nullable=True)
    computed_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)


class AnalyticsTrend(Base):
    __tablename__ = "analytics_trends"
    __table_args__ = (
        Index("idx_analytics_trends_type", "metric_type"),
        Index("idx_analytics_trends_dimension", "dimension", "dimension_value"),
        Index("idx_analytics_trends_period", "period_date"),
        {"schema": "analytics"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String(50), nullable=False)
    dimension = Column(String(50), nullable=False)
    dimension_value = Column(String(200), nullable=True)
    period_date = Column(TIMESTAMP, nullable=True)
    value = Column(Float, nullable=True)
    computed_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)


class AnalyticsHotspot(Base):
    __tablename__ = "analytics_hotspots"
    __table_args__ = (
        Index("idx_analytics_hotspots_cluster", "cluster_id"),
        Index("idx_analytics_hotspots_crime_type", "crime_type"),
        Index("idx_analytics_hotspots_period", "period_start", "period_end"),
        {"schema": "analytics"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, nullable=False)
    center_lat = Column(Float, nullable=True)
    center_lng = Column(Float, nullable=True)
    crime_type = Column(String(200), nullable=True)
    case_count = Column(Integer, nullable=True)
    severity = Column(String(20), nullable=True)
    period_start = Column(TIMESTAMP, nullable=True)
    period_end = Column(TIMESTAMP, nullable=True)
    radius_km = Column(Float, nullable=True)
    computed_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
