from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    price = Column(Numeric, nullable=True)
    max_websites = Column(Integer, nullable=True)
    max_submissions_per_day = Column(Integer, nullable=True)
    features = Column(JSONB, nullable=True)

    # reverse: users and subscriptions
    users = relationship("User", back_populates="plan")
    subscriptions = relationship("Subscription", back_populates="plan")
