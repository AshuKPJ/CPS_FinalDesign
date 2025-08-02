# backend/app/utils/logger.py

from datetime import datetime
from app.db.models.log import Log
from sqlalchemy.orm import Session
import uuid

def log_event(db: Session, user_id: str, message: str, level: str = "INFO", campaign_id: str = None, website_id: str = None):
    log = Log(
        id=uuid.uuid4(),
        user_id=user_id,
        campaign_id=campaign_id,
        website_id=website_id,
        message=message,
        level=level,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
