# backend/app/db/models/campaign.py

import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Add at top of campaign.py
import enum

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=True)
    csv_filename = Column(String(255), nullable=True)
    started_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=True)

    user = relationship("User", back_populates="campaigns")
    logs = relationship("Log", back_populates="campaign", cascade="all, delete-orphan")
    websites = relationship("Website", back_populates="campaign", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="campaign", cascade="all, delete-orphan")

class CampaignStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"