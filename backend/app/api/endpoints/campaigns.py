from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models, schemas
from app.celery_worker import process_submission

router = APIRouter()

@router.post("/", response_model=schemas.Campaign, status_code=status.HTTP_201_CREATED)
def create_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_in: schemas.CampaignCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Create a new campaign. This will create the campaign record and
    enqueue background jobs for each website.
    """
    db_campaign = models.Campaign(
        name=campaign_in.name,
        message_template=campaign_in.message_template,
        user_id=current_user.id,
        status=models.CampaignStatus.running,
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    # Enqueue tasks for Celery
    for url in campaign_in.websites:
        process_submission.delay(db_campaign.id, url)

    return db_campaign

@router.get("/", response_model=List[schemas.Campaign])
def get_user_campaigns(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all campaigns for the current user.
    """
    campaigns = db.query(models.Campaign).filter(models.Campaign.user_id == current_user.id).offset(skip).limit(limit).all()
    return campaigns

@router.get("/{campaign_id}", response_model=schemas.Campaign)
def get_campaign_details(
    campaign_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get details for a specific campaign, including its logs.
    """
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.user_id != current_user.id and current_user.role == models.UserRole.user:
        raise HTTPException(status_code=403, detail="Not authorized to view this campaign")
    return campaign