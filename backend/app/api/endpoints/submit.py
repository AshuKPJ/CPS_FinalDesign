from __future__ import annotations

import os
import traceback
import uuid
from typing import Dict, Any

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    Request,
    BackgroundTasks,
    HTTPException,
)
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.log_stream import event_generator, log
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.db.models.user_contact_profile import UserContactProfile
from app.db.models.user import User

router = APIRouter(tags=["Submit"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _row_to_dict(row) -> Dict[str, Any]:
    if not row:
        return {}
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

@router.post("/start")
async def start_submission(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    proxy: str = Form(""),
    haltOnCaptcha: bool = Form(True),
    message: str = Form(""),
    useCaptcha: bool = Form(False),
    showBrowser: bool = Form(False),   # <-- NEW: show real browser window
    trace: bool = Form(False),         # <-- NEW: record Playwright trace.zip
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rid = str(uuid.uuid4())[:8]
    log("")
    log("==============================================")
    log(f"▶️  [{rid}] /submit/start invoked")

    if not file:
        raise HTTPException(status_code=400, detail="CSV file is required")

    # Save uploaded CSV
    file_path = os.path.join(UPLOAD_DIR, f"websites_{rid}.csv")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Build user_profile (include CAPTCHA creds if present)
    user_profile: Dict[str, Any] = {}
    try:
        profile_row = (
            db.query(UserContactProfile)
            .filter(UserContactProfile.user_id == current_user.id)
            .first()
        )
        user_profile = _row_to_dict(profile_row) if profile_row else {}
    except Exception:
        user_profile = {}

    # Minimum identity fallbacks
    user_profile.setdefault("first_name", getattr(current_user, "first_name", "") or "")
    user_profile.setdefault("last_name", getattr(current_user, "last_name", "") or "")
    user_profile.setdefault("email", getattr(current_user, "email", "") or "")
    if message and message.strip():
        user_profile["message"] = message.strip()

    # Optional per-user CAPTCHA creds
    for fld in ("captcha_username", "captcha_password"):
        val = getattr(current_user, fld, None)
        if val:
            user_profile[fld] = val

    log(
        f"Options: proxy={bool(proxy)} haltOnCaptcha={haltOnCaptcha} "
        f"useCaptcha={useCaptcha} msg_len={len(message or '')}"
    )

    def run_worker(
        rid_local: str,
        csv_path: str,
        proxy_opt: str,
        halt: bool,
        msg: str,
        use_cap: bool,
        owner_id,
        show_browser: bool,
        do_trace: bool,
    ):
        from app.automation.core.runner import process_csv_and_submit
        try:
            process_csv_and_submit(
                csv_path=csv_path,
                proxy=proxy_opt,
                halt_on_captcha=halt,
                message=msg,
                user_profile=user_profile,
                use_captcha_solver=use_cap,
                headless=show_browser,                      # <-- pass through
                browser_name=os.getenv("BROWSER", "firefox"),   # env override if needed
                trace=do_trace,                                 # <-- pass through
            )
            log(f"[{rid_local}] ✅ Background worker finished")
        except Exception as e:
            log("==============================================")
            log(f"[{rid_local}] 🔥 Background worker crashed: {e}")
            log(traceback.format_exc())
            log("==============================================")

    background_tasks.add_task(
        run_worker,
        rid,
        file_path,
        proxy,
        haltOnCaptcha,
        message,
        useCaptcha,
        current_user.id,
        showBrowser,
        trace,
    )

    return JSONResponse({"message": "started", "request_id": rid})

@router.head("/logs/stream")
def logs_stream_head() -> Response:
    return Response(status_code=200)

@router.get("/logs/stream")
async def logs_stream(request: Request):
    resp = event_generator(request)
    if hasattr(resp, "__await__"):
        return await resp
    return resp
