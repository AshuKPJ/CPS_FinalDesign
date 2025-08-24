from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id", ondelete="CASCADE"), nullable=True)

    level = Column(String(20), nullable=True)
    message = Column(Text, nullable=False)
    context = Column(JSONB, nullable=True)
    timestamp = Column(None, nullable=True)  # TIMESTAMP WITH TIME ZONE per Excel

    user = relationship("User", back_populates="logs")
    campaign = relationship("Campaign", back_populates="logs")
    website = relationship("Website", back_populates="logs")
