# app/utils/db_logger.py
from __future__ import annotations

import os
import json
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, Any, Tuple, List

from sqlalchemy import Table, MetaData, inspect, text
from sqlalchemy.orm import Session

from app.db.database import SessionLocal

# Toggle DB developer logging via env var (off by default)
DB_DEVLOG = os.getenv("DB_DEVLOG", "0") == "1"

# Preferred JSON-ish column names we'll try in order.
_JSON_COL_CANDIDATES = ("meta", "details", "payload", "extra", "data")

# Preferred columns (optional) we map into if they exist.
_OPTIONAL_COLS = (
    "rid", "level", "event", "event_type", "website_id", "campaign_id",
    "user_id", "submission_id",
)

@lru_cache(maxsize=8)
def _reflect_table(bind, table_name: str) -> Optional[Table]:
    meta = MetaData()
    try:
        return Table(table_name, meta, autoload_with=bind)
    except Exception:
        return None

def _get_json_col(table: Table) -> Optional[str]:
    for c in _JSON_COL_CANDIDATES:
        if c in table.c:
            return c
    return None

def _filter_values(table: Table, values: Dict[str, Any]) -> Dict[str, Any]:
    """Keep only keys that are actual columns in `table`."""
    return {k: v for k, v in values.items() if k in table.c}

def _choose_table(session: Session, prefer_submission: bool) -> Optional[Table]:
    bind = session.get_bind()
    if prefer_submission:
        t = _reflect_table(bind, "submission_logs")
        if t is not None:
            return t
    # fallback to 'logs'
    return _reflect_table(bind, "logs")

def devlog(
    *,
    message: str,
    level: str = "INFO",
    event: Optional[str] = None,      # e.g. "NAVIGATE", "FORM_FILL", "CAPTCHA"
    rid: Optional[str] = None,        # run id (request id) to correlate a run
    user_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
    website_id: Optional[int] = None,
    submission_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,  # structured payload
) -> None:
    """
    Write a developer log row to DB if DB_DEVLOG=1 and a suitable table exists.
    - Uses `submission_logs` when `submission_id` is provided and that table exists,
      otherwise uses `logs`.
    - Only writes fields/columns that actually exist in your table.
    """
    if not DB_DEVLOG:
        return

    session: Optional[Session] = None
    try:
        session = SessionLocal()
        prefer_submission = submission_id is not None
        table = _choose_table(session, prefer_submission=prefer_submission)
        if table is None:
            # No suitable table found; silently skip
            return

        row: Dict[str, Any] = {
            "message": message,
        }

        # Optional columns if present in target table:
        opt_vals = {
            "rid": rid,
            "level": level,
            "event": event,
            "event_type": event,
            "user_id": user_id,
            "campaign_id": campaign_id,
            "website_id": website_id,
            "submission_id": submission_id,
        }
        for k in _OPTIONAL_COLS:
            v = opt_vals.get(k)
            if v is not None and k in table.c:
                row[k] = v

        # Add created_at if column exists
        if "created_at" in table.c:
            row["created_at"] = datetime.utcnow()

        # Put JSON payload into the first JSON-ish column we can find; otherwise fold into message
        if details:
            json_col = _get_json_col(table)
            if json_col:
                row[json_col] = json.dumps(details, ensure_ascii=False)
            else:
                # Safe fallback: append JSON to the message string
                row["message"] = f"{row['message']} | details={json.dumps(details, ensure_ascii=False)}"

        row = _filter_values(table, row)

        ins = table.insert().values(**row)
        session.execute(ins)
        session.commit()
    except Exception:
        if session:
            session.rollback()
        # Fail silently – dev DB logging should never break the run
    finally:
        if session:
            session.close()
