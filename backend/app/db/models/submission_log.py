from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class SubmissionLog(Base):
    __tablename__ = "submission_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)
    target_url = Column(String, nullable=False)  # Excel shows character varying, length unspecified
    status = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    processed_at = Column(None, nullable=True)  # TIMESTAMP WITH TIME ZONE

    campaign = relationship("Campaign", back_populates="submission_logs")
