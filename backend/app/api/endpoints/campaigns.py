from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models, schemas
from app.celery_worker import process_submission  # keep if you use Celery

router = APIRouter()

@router.post("/", response_model=schemas.Campaign, status_code=status.HTTP_201_CREATED)
def create_campaign(
    *,
    db: Session = Depends(deps.get_db),
    campaign_in: schemas.CampaignCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Create a new campaign and enqueue background jobs for each website.
    """
    db_campaign = models.Campaign(
        name=campaign_in.name,
        user_id=current_user.id,
        status="running",  # use string; enum not present in models
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    for url in campaign_in.websites:
        try:
            process_submission.delay(db_campaign.id, url)  # optional if Celery present
        except Exception:
            pass  # avoid breaking HTTP if worker not configured

    return db_campaign

@router.get("/", response_model=List[schemas.Campaign])
def get_user_campaigns(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    return (
        db.query(models.Campaign)
        .filter(models.Campaign.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.get("/{campaign_id}", response_model=schemas.Campaign)
def get_campaign_details(
    campaign_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.user_id != current_user.id and (current_user.role or "user") == "user":
        raise HTTPException(status_code=403, detail="Not authorized to view this campaign")
    return campaign
