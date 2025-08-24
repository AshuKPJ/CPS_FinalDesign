from sqlalchemy import Column, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id", ondelete="CASCADE"), nullable=True)

    # Excel columns
    success = Column(Boolean, nullable=True)
    response_status = Column(Integer, nullable=True)
    submitted_at = Column(None, nullable=True)  # TIMESTAMP WITHOUT TIME ZONE
    form_fields_sent = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="submissions")
    website = relationship("Website", back_populates="submissions")
