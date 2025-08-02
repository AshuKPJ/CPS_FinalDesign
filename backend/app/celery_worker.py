from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import models, schemas
from app.db.database import SessionLocal
from app.services.automation import find_and_submit_form
import asyncio

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery_app.conf.update(
    task_track_started=True,
)

@celery_app.task(name="process_submission")
def process_submission(campaign_id: int, url: str):
    """
    Celery task to process a single URL submission.
    """
    db: Session = SessionLocal()
    try:
        campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
        if not campaign or not campaign.owner or not campaign.owner.contact_info:
            # Cannot proceed without campaign or user data
            return

        user = campaign.owner
        user_contact_data = schemas.ContactInfo.from_orm(user.contact_info).dict()
        user_contact_data['email'] = user.email
        user_contact_data['first_name'] = user.first_name
        user_contact_data['last_name'] = user.last_name

        # Create a log entry
        log = models.SubmissionLog(
            campaign_id=campaign_id,
            target_url=url,
            status=models.SubmissionStatus.pending
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        # Run the async Playwright function
        result = asyncio.run(find_and_submit_form(url, user_contact_data, campaign.message_template))
        
        # Update the log with the result
        log.status = result['status']
        log.details = result['details']
        db.commit()

    finally:
        db.close()