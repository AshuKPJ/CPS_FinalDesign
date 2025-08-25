# backend/app/automation/core/runner.py
from __future__ import annotations

import csv
import json
import os
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.log_stream import log
from app.automation.core.engine import launch_browser, close_browser
from app.automation.core.config import SCREENSHOTS_DIR
from app.automation.filling.submitter import process_single_site


def _wire_visibility(page):
    """Minimal visibility. Comment out lines if you want even less."""
    try:
        page.on("console", lambda msg: log(f"[CONSOLE] {msg.type}: {msg.text}"))
    except Exception:
        pass
    try:
        page.on("request", lambda req: log(f"[REQ] {req.method} {req.url}"))
        page.on("response", lambda resp: log(f"[RES] {resp.status} {resp.url}"))
    except Exception:
        pass


def _is_header_like(s: str) -> bool:
    s = (s or "").replace("\ufeff", "").strip().lower()
    return s in {"website", "url", "domain", "site"}


def _code_line(res: Dict[str, Any]) -> str:
    """Return a concise, human-readable one-liner for logs."""
    host = urllib.parse.urlparse(res.get("final_url") or "").netloc or (res.get("input_url") or "")
    method = res.get("method") or "none"
    status = res.get("status") or "skipped"
    reason = (res.get("reason") or "").strip()

    if method == "form" and status == "success":
        code = "FORM_SUCCESS"
    elif method == "form" and status == "fail":
        code = f"FORM_FAIL({reason or 'unknown'})"
    elif method == "email" and status == "email_only":
        code = f"EMAIL_ONLY({len(res.get('emails') or [])})"
    elif status == "nav_fail":
        code = f"NAV_FAIL({reason or 'error'})"
    else:
        code = "SKIPPED"

    return f"[{res.get('idx')}] {host} — {code}"


def _write_reports(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = SCREENSHOTS_DIR / f"summary_{ts}.csv"
    json_path = SCREENSHOTS_DIR / f"summary_{ts}.json"

    # Normalize fields for CSV
    fields = [
        "idx", "input_url", "final_url", "method", "status", "reason", "emails_count",
        "shot_loaded", "shot_contact", "shot_captcha", "shot_submit_error", "shot_postsubmit", "shot_nav_fail",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            r = dict(r)
            r["emails_count"] = len(r.get("emails") or [])
            shots = r.get("shots") or {}
            r["shot_loaded"] = shots.get("loaded") or ""
            r["shot_contact"] = shots.get("contact") or ""
            r["shot_captcha"] = shots.get("captcha") or ""
            r["shot_submit_error"] = shots.get("submit_error") or ""
            r["shot_postsubmit"] = shots.get("postsubmit") or ""
            r["shot_nav_fail"] = shots.get("nav_fail") or ""
            w.writerow({k: r.get(k, "") for k in fields})

    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)

    log(f"Report: {csv_path}")
    log(f"Report: {json_path}")


def process_csv_and_submit(
    csv_path: str,
    proxy: str,
    halt_on_captcha: bool,
    message: str,
    user_profile: Optional[Dict[str, Any]],
    use_captcha_solver: bool,
    headless: Optional[bool] = True,
    browser_name: Optional[str] = None,
    trace: bool = False,
) -> None:
    """Main runner: iterate rows → process_single_site → concise logs + summary + reports."""
    browser_name = browser_name or os.getenv("BROWSER", "firefox")

    context = page = browser = p = None
    tracing = False
    trace_path = None
    results: List[Dict[str, Any]] = []
    try:
        context, page, browser, p = launch_browser(
            proxy=proxy,
            headless=headless,
            browser_name=browser_name,
        )
        _wire_visibility(page)

        if trace or os.getenv("TRACE") == "1":
            try:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                trace_path = SCREENSHOTS_DIR / f"trace_{ts}.zip"
                context.tracing.start(screenshots=True, snapshots=True, sources=True)
                tracing = True
                log(f"Tracing enabled → will save: {trace_path}")
            except Exception as e:
                log(f"Could not start tracing: {e}")

        path = Path(csv_path)
        if not path.exists():
            log(f"CSV not found: {csv_path}")
            return

        with path.open("r", newline="", encoding="utf-8") as fh:
            rdr = csv.reader(fh)
            for idx, row in enumerate(rdr, 1):
                raw = (row[0] or "").strip() if row else ""
                if not raw or _is_header_like(raw):
                    continue

                res = process_single_site(
                    page=page,
                    raw_url=raw,
                    idx=idx,
                    screenshots_dir=SCREENSHOTS_DIR,
                    halt_on_captcha=halt_on_captcha,
                    message=message,
                    user_profile=user_profile or {},
                    use_captcha_solver=use_captcha_solver,
                )
                results.append(res)
                log(_code_line(res))

        # Summary
        form_success = sum(1 for r in results if r.get("method") == "form" and r.get("status") == "success")
        form_fail    = sum(1 for r in results if r.get("method") == "form" and r.get("status") == "fail")
        email_only   = sum(1 for r in results if r.get("status") == "email_only")
        skipped      = sum(1 for r in results if r.get("status") == "skipped")
        nav_fail     = sum(1 for r in results if r.get("status") == "nav_fail")
        total        = len(results)

        log("=== Summary ===")
        log(f"form_success={form_success} | form_fail={form_fail} | email_only={email_only} | skipped={skipped} | nav_fail={nav_fail} | total={total}")

        _write_reports(results)

    finally:
        if tracing:
            try:
                context.tracing.stop(path=str(trace_path))
                log(f"Trace saved: {trace_path}")
                log("Open trace with: playwright show-trace " + str(trace_path))
            except Exception as e:
                log(f"Could not stop/save trace: {e}")
        close_browser(context, browser, p)
