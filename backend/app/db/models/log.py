# backend/app/db/models/log.py

import uuid
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"))
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"))
    level = Column(String(20), nullable=True)
    message = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="logs")
    campaign = relationship("Campaign", back_populates="logs")
    website = relationship("Website", back_populates="logs")
