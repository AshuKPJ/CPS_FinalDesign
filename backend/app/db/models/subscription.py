# backend/app/db/models/subscription.py

import uuid
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    user = relationship("User")
    plan = relationship("SubscriptionPlan")
