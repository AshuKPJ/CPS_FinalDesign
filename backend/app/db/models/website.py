# backend/app/db/models/website.py

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Website(Base):
    __tablename__ = "websites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    website_url = Column(String, nullable=False)
    domain = Column(String, nullable=True)
    contact_page_url = Column(String, nullable=True)
    has_contact_form = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="websites")
    user = relationship("User", back_populates="websites")
    submissions = relationship("Submission", back_populates="website", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="website", cascade="all, delete-orphan")
