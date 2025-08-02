# backend/app/db/models/submission_log.py

import uuid
import enum
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    form_not_found = "form_not_found"
    email_found = "email_found"
    captcha_failed = "captcha_failed"
    submission_failed = "submission_failed"

class SubmissionLog(Base):
    __tablename__ = "submission_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    target_url = Column(String, nullable=False)
    status = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    processed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
