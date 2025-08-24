from sqlalchemy import Column, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Setting(Base):
    __tablename__ = "settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    default_message_template = Column(Text, nullable=True)
    captcha_api_key = Column(Text, nullable=True)
    proxy_url = Column(Text, nullable=True)
    auto_submit = Column(Boolean, nullable=True)

    user = relationship("User", back_populates="settings")
