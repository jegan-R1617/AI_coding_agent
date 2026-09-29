"""
SQLAlchemy schema definitions for the Multi-Agent Code Pipeline.
Contains only the Error table used for centralized error logging.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ErrorLog(Base):
    """Database table for storing application error logs."""

    __tablename__ = "error_logs"

    error_id = Column(Integer, primary_key=True)
    error_uuid = Column(UUID, server_default=text("gen_random_uuid()"), unique=True, index=True)
    error_code = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    function_name = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    is_active = Column(Boolean, server_default=text("True"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_by = Column(String, server_default=text("'SYSTEM'"))
    updated_at = Column(DateTime, nullable=True)
    updated_by = Column(String, nullable=True)
