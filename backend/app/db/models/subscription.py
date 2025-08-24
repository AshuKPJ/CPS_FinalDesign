from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True)

    external_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    start_date = Column(None, nullable=True)  # TIMESTAMP WITHOUT TIME ZONE
    end_date = Column(None, nullable=True)

    user = relationship("User", back_populates="subscriptions_rel")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
