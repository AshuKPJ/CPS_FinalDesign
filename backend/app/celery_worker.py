from __future__ import annotations
from celery import Celery
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import models
from app.db.database import SessionLocal
from app.log_stream import log
from app.automation.core.engine import launch_browser, close_browser
from app.automation.filling.submitter import process_single_site
from app.automation.core.config import SCREENSHOTS_DIR, DBC_USER, DBC_PASS

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)
celery_app.conf.update(task_track_started=True)

@celery_app.task(name="process_submission")
def process_submission(campaign_id: str, url: str, halt_on_captcha: bool = True, message: str = ""):
    db: Session = SessionLocal()
    try:
        campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
        if not campaign:
            log(f"[Celery] Campaign {campaign_id} not found")
            return

        user = db.query(models.User).filter(models.User.id == campaign.user_id).first()
        if not user:
            log(f"[Celery] Owner user for campaign {campaign_id} not found")
            return

        user_profile = {
            "first_name": getattr(user, "first_name", "") or "",
            "last_name": getattr(user, "last_name", "") or "",
            "email": getattr(user, "email", "") or "",
        }
        if message:
            user_profile["message"] = message

        # Try per-user creds; if missing, env fallback
        u_user = getattr(user, "captcha_username", "") or ""
        u_pass = getattr(user, "captcha_password", "") or ""  # if stored plain; else leave blank
        use_solver = bool((u_user and u_pass) or (DBC_USER and DBC_PASS))
        if u_user and u_pass:
            user_profile["captcha_username"] = u_user
            user_profile["captcha_password"] = u_pass

        # Log row
        slog = models.SubmissionLog(campaign_id=campaign_id, target_url=url, status="pending")
        db.add(slog); db.commit(); db.refresh(slog)

        context, page, browser, p = launch_browser(proxy="")
        try:
            result = process_single_site(
                page=page,
                raw_url=url,
                idx=1,
                screenshots_dir=SCREENSHOTS_DIR,
                halt_on_captcha=halt_on_captcha,
                message=message or "",
                user_profile=user_profile,
                use_captcha_solver=use_solver,
            )
        finally:
            close_browser(context, browser, p)

        status_map = {"form_success":"success","form_fail":"failed","email_only":"emailed","nav_fail":"failed","skipped":"skipped"}
        slog.status = status_map.get(result.get("status"), "failed")
        slog.details = result.get("reason") or ""
        db.commit()
        log(f"[Celery] {url} → {slog.status} ({slog.details})")

    except Exception as e:
        log(f"[Celery] Error while processing {url}: {e}")
    finally:
        db.close()
