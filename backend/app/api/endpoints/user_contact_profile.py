# backend/app/api/endpoints/user_contact_profile.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.db import models, schemas
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/contact-answers", response_model=schemas.UserContactProfileOut)
def get_user_contact_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    print("✅ Authenticated user:", current_user.id)

    profile = db.query(models.UserContactProfile).filter_by(user_id=current_user.id).first()
    
    if profile:
        print("✅ Found profile in DB")
        return profile

    print("⚠️ No profile found, using fallback...")

    try:
        fallback = schemas.UserContactProfileOut(
            id=current_user.id,
            user_id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            company_name=None,
            job_title=None,
            phone_number=None,
            website_url=None,
            subject=None,
            referral_source=None,
            message=None,
            preferred_contact=None,
            city=None,
            state=None,
            industry=None,
            best_time_to_contact=None,
            budget_range=None,
            product_interest=None,
            is_existing_customer=False,
            country=None,
            language=None,
            timezone=None,
            linkedin_url=None,
            notes=None,
            form_custom_field_1=None,
            form_custom_field_2=None,
            form_custom_field_3=None,
            contact_source=None,
            preferred_language=None,
            region=None,
            zip_code=None,
        )
        print("✅ Fallback returned")
        return fallback
    except Exception as e:
        print("❌ Error building fallback:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal fallback error: {str(e)}")


@router.post("/upsert", response_model=schemas.UserContactProfileOut)
def upsert_user_contact_profile(
    data: schemas.UserContactProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    profile = (
        db.query(models.UserContactProfile)
        .filter(models.UserContactProfile.user_id == current_user.id)
        .first()
    )

    # Remove user_id if present in data
    data_dict = data.dict(exclude={"user_id"}, exclude_unset=True)

    if profile:
        for field, value in data_dict.items():
            setattr(profile, field, value)
    else:
        profile = models.UserContactProfile(**data_dict, user_id=current_user.id)
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile
