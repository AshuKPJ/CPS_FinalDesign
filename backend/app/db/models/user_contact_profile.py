# app/db/models/user_contact_profile.py

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid

class UserContactProfile(Base):
    __tablename__ = "user_contact_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_contact_profiles_user_id"),
        Index("ix_user_contact_profiles_user_id", "user_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    company_name = Column(String(150), nullable=True)
    job_title = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    phone_number = Column(String(50), nullable=True)
    website_url = Column(String(200), nullable=True)
    subject = Column(String(200), nullable=True)
    referral_source = Column(String(200), nullable=True)
    message = Column(Text, nullable=True)
    preferred_contact = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    best_time_to_contact = Column(String(100), nullable=True)
    budget_range = Column(String(100), nullable=True)
    product_interest = Column(String(150), nullable=True)
    is_existing_customer = Column(Boolean, nullable=True, default=False)

    country = Column(String, nullable=True)
    language = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    form_custom_field_1 = Column(String, nullable=True)
    form_custom_field_2 = Column(String, nullable=True)
    form_custom_field_3 = Column(String, nullable=True)
    contact_source = Column(String, nullable=True)
    preferred_language = Column(String, nullable=True)
    region = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)

    user = relationship("User", back_populates="contact_profile", uselist=False)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}