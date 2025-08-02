# backend/app/api/endpoints/submit.py

from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.db.database import get_db
from app.api.deps import get_current_user
from app.automation.runner import run_campaign_automation
from app.db.models.user import User
from app.db.models.campaign import Campaign
from app.utils.logger import log_event
from app.db.models.log import Log

import pandas as pd
import tempfile
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/start")
def start_form_submission(
    file: UploadFile,
    proxy: str = Form(""),
    haltOnCaptcha: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Initiates the form submission automation process.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # ✅ Save and read the uploaded file
    try:
        contents = file.file.read().decode('utf-8')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w+", encoding="utf-8") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        df = pd.read_csv(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")

    # ✅ Clean column names
    df.columns = [col.strip() for col in df.columns]

    # ✅ Detect valid website column
    possible_columns = ["website", "Website", "domain", "url"]
    detected_col = next((col for col in possible_columns if col in df.columns), None)

    if not detected_col:
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain one of the following columns: {possible_columns}. Found: {list(df.columns)}"
        )

    websites = df[detected_col].dropna().astype(str).str.strip().tolist()

    if not websites:
        raise HTTPException(status_code=400, detail="No valid website URLs found in the CSV.")

    # ✅ Create campaign
    campaign_id = str(uuid.uuid4())
    campaign = Campaign(
        id=campaign_id,
        user_id=current_user.id,
        name=f"Campaign - {file.filename}",
        csv_filename=file.filename,
        started_at=datetime.utcnow(),
        status="started"
    )
    db.add(campaign)
    db.commit()

    # ✅ Log creation
    log_event(
        db=db,
        user_id=str(current_user.id),
        message=f"✅ Campaign created and file parsed using '{detected_col}' column.",
        campaign_id=campaign_id
    )

    # ✅ Trigger automation
    run_campaign_automation(
        websites=websites,
        proxy=proxy,
        halt_on_captcha=haltOnCaptcha,
        user_id=str(current_user.id),
        campaign_id=campaign_id,
        db=db
    )

    return JSONResponse(content={
        "message": "✅ Campaign submission started.",
        "campaign_id": campaign_id,
        "total_websites": len(websites)
    })


@router.get("/logs/latest")
def get_latest_submission_logs(
    limit: int = 50,
    campaign_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns latest log lines for the current user and optional campaign.
    """
    query = db.query(Log).filter(Log.user_id == current_user.id)
    if campaign_id:
        query = query.filter(Log.campaign_id == campaign_id)

    logs = query.order_by(Log.timestamp.desc()).limit(limit).all()
    return logs
