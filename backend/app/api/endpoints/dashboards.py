from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api import deps
from app.db import models

router = APIRouter()

@router.get("/owner-stats")
def get_owner_dashboard_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_owner_user),
):
    """
    Get high-level platform statistics for the Owner dashboard.
    """
    total_users = db.query(func.count(models.User.id)).scalar()
    total_campaigns = db.query(func.count(models.Campaign.id)).scalar()
    
    successful_submissions = db.query(func.count(models.SubmissionLog.id)).filter(
        models.SubmissionLog.status == models.SubmissionStatus.success
    ).scalar()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_last_30_days = db.query(func.count(models.User.id)).filter(
        models.User.created_at >= thirty_days_ago
    ).scalar()

    return {
        "total_users": total_users,
        "total_campaigns": total_campaigns,
        "successful_submissions": successful_submissions,
        "new_users_last_30_days": new_users_last_30_days,
    }
