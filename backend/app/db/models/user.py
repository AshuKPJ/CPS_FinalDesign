# backend/app/db/models/user.py
from sqlalchemy import Column, String, Boolean, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from enum import Enum
from .subscription_plan import SubscriptionPlan
from .campaign import Campaign
from .submission import Submission
from .log import Log
from .website import Website
from .user_contact_profile import UserContactProfile

from app.db.base_class import Base

# ✅ Define role choices for consistency across schema and API
class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    owner = "owner"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)

    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=True)
    subscription_status = Column(String(50), nullable=True)
    subscription_start = Column(TIMESTAMP, nullable=True)
    subscription_end = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    profile_image_url = Column(Text, nullable=True)

    role = Column(String(20), server_default=UserRole.user.value, nullable=True)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    captcha_username = Column(Text, nullable=True)
    captcha_password_hash = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)

    # ✅ Relationships
    plan = relationship("SubscriptionPlan", back_populates="users")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")
    websites = relationship("Website", back_populates="user", cascade="all, delete-orphan")
    #contact_profile = relationship("UserContactProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    contact_profile = relationship("UserContactProfile", back_populates="user", uselist=False)
