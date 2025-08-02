from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return {
        "total_submissions": 120,
        "captcha_failures": 10,
        "no_contact_page": 15,
        "success_rate": 87.5
    }

@router.get("/monthly-submissions")
def monthly_submissions():
    return [
        {"month": "January", "count": 25},
        {"month": "February", "count": 40},
        {"month": "March", "count": 55},
        {"month": "April", "count": 35},
    ]

@router.get("/weekly-activity")
def weekly_activity():
    return [
        {"week": "Week 1", "count": 15},
        {"week": "Week 2", "count": 22},
        {"week": "Week 3", "count": 19},
        {"week": "Week 4", "count": 28},
    ]

@router.get("/submission-results")
def submission_results():
    return [
        {"label": "Success", "value": 87},
        {"label": "Captcha Failed", "value": 10},
        {"label": "No Contact Page", "value": 3},
    ]
