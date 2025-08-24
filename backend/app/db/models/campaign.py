from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=True)
    csv_filename = Column(String(255), nullable=True)
    started_at = Column(None, nullable=True)  # TIMESTAMP WITHOUT TIME ZONE
    status = Column(String(50), nullable=True)

    user = relationship("User", back_populates="campaigns")
    websites = relationship("Website", back_populates="campaign")
    submission_logs = relationship("SubmissionLog", back_populates="campaign")
    logs = relationship("Log", back_populates="campaign")
