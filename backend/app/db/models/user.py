from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)

    # ✅ align to what auth.py expects
    hashed_password = Column(Text, nullable=False)

    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True)

    subscription_status = Column(String(50), nullable=True)
    subscription_start = Column(None, nullable=True)
    subscription_end = Column(None, nullable=True)
    created_at = Column(None, nullable=True)

    profile_image_url = Column(Text, nullable=True)
    role = Column(String(20), nullable=True, default="user")
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    captcha_username = Column(Text, nullable=True)
    captcha_password_hash = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)

    plan = relationship("SubscriptionPlan", back_populates="users", lazy="joined")
    campaigns = relationship("Campaign", back_populates="user")
    websites = relationship("Website", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    subscriptions_rel = relationship("Subscription", back_populates="user")
    settings = relationship("Setting", back_populates="user", uselist=False)
    user_contact_profile = relationship("UserContactProfile", back_populates="user", uselist=False)
    logs = relationship("Log", back_populates="user")
