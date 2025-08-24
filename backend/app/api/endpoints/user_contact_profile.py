from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.db.models.user_contact_profile import UserContactProfile
from app.db.models.user import User
from app.db import schemas

router = APIRouter(prefix="/usercontactprofile", tags=["user_contact_profile"])

@router.get("/contact-answers", response_model=schemas.UserContactProfileOut)
def get_contact_answers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    uid = UUID(str(current_user.id))

    prof = db.query(UserContactProfile).filter(UserContactProfile.user_id == uid).first()
    if prof is None and current_user.email:
        prof = (
            db.query(UserContactProfile)
            .filter(func.lower(UserContactProfile.email) == current_user.email.lower())
            .first()
        )
    if prof:
        return prof

    # stitched minimal fallback (no DB insert here)
    return schemas.UserContactProfileOut(
        id=uid, user_id=uid,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
    )

@router.post("/upsert", response_model=schemas.UserContactProfileOut)
def upsert_contact_answers(
    payload: schemas.UserContactProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    uid = UUID(str(current_user.id))
    prof = db.query(UserContactProfile).filter(UserContactProfile.user_id == uid).first()
    if not prof:
        prof = UserContactProfile(user_id=uid)

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(prof, k, v)

    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof
