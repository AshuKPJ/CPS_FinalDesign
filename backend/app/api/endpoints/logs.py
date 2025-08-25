from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import LogEvent
from app.schemas import LogListOut, LogOut

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("", response_model=LogListOut)
def list_logs(
    job_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(LogEvent)
    if job_id: q = q.filter(LogEvent.job_id == job_id)
    if campaign_id: q = q.filter(LogEvent.campaign_id == campaign_id)
    if level: q = q.filter(LogEvent.level == level)

    total = q.count()
    rows = q.order_by(LogEvent.id.desc()).offset(offset).limit(limit).all()
    items = [
        LogOut(
            id=r.id,
            ts=r.ts.isoformat(timespec="seconds"),
            level=r.level,
            job_id=r.job_id,
            campaign_id=r.campaign_id,
            message=r.message,
        )
        for r in rows
    ]
    return {"total": total, "items": items}
