from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse, JSONResponse
import os, threading, traceback
from sqlalchemy.orm import Session

from app.log_stream import event_generator, log
from app.automation.browser_job import process_csv_and_submit
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.db.models.user_contact_profile import UserContactProfile
from app.db.models.user import User

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _row_to_dict(row) -> dict:
    if not row:
        return {}
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

def _summarize_profile(prefix: str, d: dict):
    non_empty = {k: v for k, v in d.items() if v not in (None, "", False)}
    log(f"{prefix}: {len(non_empty)} non-empty fields")
    shown = 0
    for k, v in non_empty.items():
        s = str(v)
        if len(s) > 200:
            s = s[:200] + "…"
        log(f"  · {k}: {s}")
        shown += 1
        if shown >= 20:
            log("  · …(truncated)")
            break

@router.post("/start")
async def start_submission(
    file: UploadFile = File(...),
    proxy: str = Form(""),
    haltOnCaptcha: bool = Form(True),
    message: str = Form(""),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    # Save CSV
    file_path = os.path.join(UPLOAD_DIR, "websites.csv")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # --- Deep auth / DB logs
    user_id = str(current_user.id)
    log("----------------------------------------------")
    log("Start request received")
    log(f"Saved CSV to: {file_path}")
    log(f"Proxy: {proxy}")
    log(f"Halt on captcha: {haltOnCaptcha}")
    log(f"Message length: {len(message or '')}")
    log(f"Resolved user_id (from auth): {user_id}")

    # Load contact profile for this user
    profile_row = (
        db.query(UserContactProfile)
        .filter(UserContactProfile.user_id == current_user.id)
        .first()
    )
    user_profile = _row_to_dict(profile_row)

    if user_profile:
        _summarize_profile("Loaded user_contact_profile", user_profile)
    else:
        log("No user_contact_profiles row found for this user; falling back to basic user fields.")

        # Fallback: pull basic fields from users table
        user_row = db.query(User).filter(User.id == current_user.id).first()
        fallback = {}
        if user_row:
            fallback = {
                "first_name": user_row.first_name or "",
                "last_name": user_row.last_name or "",
                "email": user_row.email or "",
            }
        user_profile = fallback
        if user_profile:
            _summarize_profile("Fallback (users table)", user_profile)
        else:
            log("Fallback produced no data (unexpected).")

    log("----------------------------------------------")

    # Detach long-running job
    def _worker():
        try:
            # ensure message is present in the dict if user typed one
            profile = dict(user_profile or {})
            if message and message.strip():
                profile["message"] = message.strip()

            process_csv_and_submit(
                csv_path=file_path,
                proxy=proxy,
                halt_on_captcha=haltOnCaptcha,
                message=message,
                user_profile=profile,
            )
        except Exception as e:
            log("==============================================")
            log("Background job crashed")
            log("----------------------------------------------")
            log(str(e))
            log(traceback.format_exc())
            log("==============================================")

    threading.Thread(target=_worker, daemon=True).start()
    return JSONResponse({"message": "started"})

@router.get("/logs/stream")
async def stream_logs(request):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")
