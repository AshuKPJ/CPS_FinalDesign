# backend/app/api/endpoints/submit.py

from fastapi import APIRouter, UploadFile, File, Form, Request, Depends
from fastapi.responses import StreamingResponse, JSONResponse
import os, threading, traceback
from sqlalchemy.orm import Session
from app.log_stream import event_generator, log
from app.automation.browser_job import process_csv_and_submit
from app.db.database import get_db
from app.db.models.user_contact_profile import UserContactProfile
# If you already have an auth dep that returns the current user, use it:
# from app.api.deps import get_current_user

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def profile_to_dict(rec: UserContactProfile | None) -> dict:
    if not rec:
        return {}
    # Convert SQLAlchemy row to a plain dict
    return {c.name: getattr(rec, c.name) for c in rec.__table__.columns}

@router.post("/start")
async def start_submission(
    request: Request,
    file: UploadFile = File(...),
    proxy: str = Form(""),
    haltOnCaptcha: bool = Form(True),
    message: str = Form(""),
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user),   # preferred if available
):
    # 1) Save the CSV
    file_path = os.path.join(UPLOAD_DIR, "websites.csv")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 2) Resolve the logged-in user id
    user_id = None
    # If you have `current_user`, do: user_id = str(current_user.id)
    if hasattr(request, "state") and hasattr(request.state, "user"):
        u = request.state.user
        if isinstance(u, dict):
            user_id = u.get("sub") or u.get("id")
        else:
            user_id = getattr(u, "sub", None) or getattr(u, "id", None)

    # 3) Load the user's contact profile from DB
    user_profile = {}
    if user_id:
        rec = db.query(UserContactProfile).filter(UserContactProfile.user_id == user_id).first()
        user_profile = profile_to_dict(rec)

    # 4) Log a short preview so you can see it worked
    log("----------------------------------------------")
    log("Start request received")
    log(f"Saved CSV to: {file_path}")
    log(f"Proxy: {proxy}")
    log(f"Halt on captcha: {haltOnCaptcha}")
    log(f"Message length: {len(message or '')}")
    if user_id:
        log(f"Resolved user_id: {user_id}")
    if user_profile:
        log("Loaded user_contact_profile (preview):")
        shown = 0
        for k, v in user_profile.items():
            if not v:
                continue
            s = str(v)
            if len(s) > 200:
                s = s[:200] + "…"
            log(f"- {k}: {s}")
            shown += 1
            if shown >= 20:
                log("…(truncated)")
                break
    else:
        log("No user profile found for this user.")
    log("----------------------------------------------")

    # 5) Run the automation fully detached (returns immediately)
    def _worker():
        try:
            process_csv_and_submit(
                csv_path=file_path,
                proxy=proxy,
                halt_on_captcha=haltOnCaptcha,
                message=message,
                user_profile=user_profile,
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
async def stream_logs(request: Request):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")
