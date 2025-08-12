# backend/app/automation/runner.py

import traceback
from pathlib import Path
from typing import List, Dict, Optional
from app.log_stream import log
from .system_utils import ensure_windows_proactor_policy
from .config import PROFILE_DIR, SCREENSHOTS_DIR, NAV_TIMEOUT_MS, BROWSER_NAME
from .csv_utils import read_csv_safely, extract_websites
from .browser_engine import launch_browser, close_browser
from .website_worker import process_single_site

def process_csv_and_submit(
    csv_path: str,
    proxy: str = "",
    halt_on_captcha: bool = True,
    message: str = "",
    user_profile: Optional[Dict] = None
) -> None:
    try:
        log("")
        log("==============================================")
        log("Starting browser automation job")
        log("==============================================")

        ensure_windows_proactor_policy()

        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        df = read_csv_safely(csv_path)
        log(f"CSV read successfully. Shape: {df.shape}")
        websites: List[str] = extract_websites(df)
        if not websites:
            log("No valid websites to process. Exiting.")
            return

        # 🔍 NEW: show the profile we’ll use (sanitized)
        profile = dict(user_profile or {})
        if profile:
            log("----------------------------------------------")
            log("Loaded user_contact_profile (sanitized):")
            for k, v in profile.items():
                if v is None or v == "":
                    continue
                # avoid logging very long values verbatim
                sv = str(v)
                if len(sv) > 200:
                    sv = sv[:200] + "…"
                log(f"- {k}: {sv}")
            log("----------------------------------------------")
        else:
            log("No user_profile provided; will fill only basic fields.")

        log("")
        log("----------------------------------------------")
        log("Step 4 - Launching Browser")
        log(f"Config - NAV_TIMEOUT_MS={NAV_TIMEOUT_MS}")
        if proxy:
            log(f"Config - PROXY={proxy}")
        log(f"Browser engine: {BROWSER_NAME}")

        context, page, browser, p = launch_browser(proxy)

        total = len(websites)
        log("----------------------------------------------")
        log(f"Step 5 - Processing Websites (total: {total})")

        success_count = 0
        fail_count = 0
        email_only_count = 0

        for idx, raw_url in enumerate(websites, start=1):
            try:
                result = process_single_site(
                    page=page,
                    raw_url=raw_url,
                    idx=idx,
                    screenshots_dir=SCREENSHOTS_DIR,
                    halt_on_captcha=halt_on_captcha,
                    message=message or profile.get("message", "") or "Hello from automation",
                    user_profile=profile,
                )
                status = result.get("status") if isinstance(result, dict) else None
                if status == "form_success":
                    success_count += 1
                elif status == "form_fail":
                    fail_count += 1
                elif status == "email_only":
                    email_only_count += 1

            except Exception as e:
                err = str(e).lower()
                is_captcha = any(k in err for k in ("captcha", "recaptcha", "hcaptcha"))
                if is_captcha and halt_on_captcha:
                    log("Possible CAPTCHA encountered; halting because halt_on_captcha=True")
                    break
                try:
                    page.screenshot(path=str(SCREENSHOTS_DIR / f"row{idx}_error.png"), full_page=False)
                except Exception:
                    pass
                log(f"Unhandled error for {raw_url}: {e}. Continuing to next URL.")
                continue

        log("----------------------------------------------")
        log(f"Automation complete: {success_count} form submissions succeeded, "
            f"{fail_count} failed, {email_only_count} contacted via email.")

        close_browser(context, browser, p)

    except Exception:
        log("")
        log("==============================================")
        log("Critical error in automation")
        log("----------------------------------------------")
        log(traceback.format_exc())
        log("==============================================")

if __name__ == "__main__":
    import sys
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else "uploads/websites.csv"
    proxy_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    halt_arg = (sys.argv[3].lower() == "true") if len(sys.argv) > 3 else True
    process_csv_and_submit(csv_arg, proxy_arg, halt_arg)
