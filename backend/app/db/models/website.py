from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Website(Base):
    __tablename__ = "websites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # from Excel
    domain = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    contact_url = Column(Text, nullable=True)
    created_at = Column(None, nullable=True)  # TIMESTAMP WITHOUT TIME ZONE (nullable per Excel)

    form_detected = Column(Boolean, nullable=True)
    form_field_count = Column(Integer, nullable=True)
    form_field_types = Column(JSONB, nullable=True)
    form_field_options = Column(JSONB, nullable=True)
    form_labels = Column(ARRAY(Text), nullable=True)
    form_name_variants = Column(ARRAY(Text), nullable=True)
    form_type = Column(String(100), nullable=True)
    has_captcha = Column(Boolean, nullable=True)
    captcha_type = Column(String(100), nullable=True)
    captcha_difficulty = Column(Text, nullable=True)
    captcha_solution_time = Column(Integer, nullable=True)
    captcha_metadata = Column(JSONB, nullable=True)
    requires_proxy = Column(Boolean, nullable=True)
    proxy_block_type = Column(Text, nullable=True)
    last_proxy_used = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)
    question_answer_fields = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="websites")
    campaign = relationship("Campaign", back_populates="websites")
    submissions = relationship("Submission", back_populates="website")
    logs = relationship("Log", back_populates="website")
