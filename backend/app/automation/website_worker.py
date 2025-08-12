# backend/app/automation/website_worker.py

from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict
from app.log_stream import log
from playwright.sync_api import Page
from .config import NAV_TIMEOUT_MS
from .popup_killer import dismiss_popups
from .contact_finder import find_contact_method
from .field_mapper import build_fill_plan

def _timestamped_base(idx: int) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"row{idx}_{ts}"

def _normalize_url(raw_url: str) -> str:
    return raw_url if raw_url.startswith(("http://", "https://")) else f"http://{raw_url}"

def process_single_site(
    page: Page,
    raw_url: str,
    idx: int,
    screenshots_dir: Path,
    halt_on_captcha: bool,
    message: str,
    user_profile: Dict  # ✅ pass the logged-in user's profile dict
) -> None:
    """
    user_profile should include keys from user_contact_profiles table.
    We'll also override its 'message' field with the provided `message` param if set.
    """
    # ensure message present
    profile = dict(user_profile or {})
    if message and message.strip():
        profile["message"] = message.strip()

    base = _timestamped_base(idx)
    url = _normalize_url(raw_url)
    log("----------------------------------------------")
    log(f"[{idx}] Target URL: {url}")

    # 1) Navigate
    loaded = False
    try:
        log("Navigating (attempt 1)")
        page.goto(url, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
        loaded = True
        log(f"Loaded: {page.url}")
    except Exception as e1:
        log(f"First navigation failed: {e1}")
        if url.startswith("http://"):
            https_url = "https://" + url[len("http://"):]
            log(f"Retry with HTTPS: {https_url}")
            try:
                page.goto(https_url, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
                loaded = True
                log(f"Loaded: {page.url}")
            except Exception as e2:
                log(f"HTTPS retry failed: {e2}")

    if not loaded:
        _shot(page, screenshots_dir / f"{base}_error.png")
        log(f"Skipping {url} after failed navigation. Moving to next URL.")
        return

    # 2) Clear popups
    try:
        dismiss_popups(page, context=page.context, accept_cookies=True, retries=2)
    except Exception:
        pass

    # 3) Discover contact method (may navigate)
    try:
        contact = find_contact_method(page)
        log(f"Contact discovery: {contact}")
    except Exception as e:
        contact = {"page_changed": False, "url": page.url, "emails": [], "form": {"has_form": False}}
        log(f"Contact discovery failed: {e}")

    # If we navigated to a contact page, clear popups again
    if contact.get("page_changed"):
        try:
            dismiss_popups(page, context=page.context, accept_cookies=True, retries=1)
        except Exception:
            pass
        _shot(page, screenshots_dir / f"{base}_contact.png")

    _shot(page, screenshots_dir / f"{base}_loaded.png")

    # 4) PRIORITY: FORM FIRST → then EMAIL (top 2)
    form_info = (contact.get("form") or {})
    emails: List[str] = contact.get("emails") or []

    if form_info.get("has_form"):
        form_index = form_info.get("index", 0)
        log("📝 Contact form detected; building fill plan from user_profile")
        plan = build_fill_plan(page, form_index, profile)
        if not plan:
            log("No fields matched from profile; will try generic minimal fill")
            # minimal fallback
            _try_fill(page, 'input[type="email" i]', profile.get("email", ""), "email")
            _try_fill(page, 'textarea', profile.get("message", ""), "message")
        else:
            for key, value, which in [(sel, val, lab) for (sel, val, lab) in plan]:
                _apply_fill(page, key, value, which)

        # one more popup sweep before submit
        try:
            dismiss_popups(page, context=page.context, accept_cookies=False, retries=1)
        except Exception:
            pass

        # submit
        submit = page.locator("form").nth(form_index).locator(
            'button[type="submit"], input[type="submit"]'
        ).first

        try:
            try:
                with page.expect_navigation(timeout=8000):
                    submit.click()
                log("Form submitted (navigation observed)")
            except Exception:
                submit.click(timeout=2000)
                page.wait_for_timeout(4000)  # AJAX
                log("Form submitted (likely AJAX, no nav)")
        except Exception as e:
            _shot(page, screenshots_dir / f"{base}_postsubmit.png")
            log(f"❌ Submit click failed: {e}")
            return

        # Post-submit evidence & strict outcome
        _shot(page, screenshots_dir / f"{base}_postsubmit.png")
        outcome, reason = _detect_submission_outcome(page, form_index)
        if outcome == "success":
            log("✅ Success message detected after form submission")
        else:
            if reason:
                log(f"❌ Form submission failed: {reason}")
            else:
                log("❌ Form submission failed: No success confirmation detected")
        return

    # No form → EMAIL path (top 2)
    if emails:
        top2 = emails[:2]
        log(f"📧 No form found. Will email top {len(top2)}: {top2}")
        _enqueue_emails(url=page.url, recipients=top2, message=profile.get("message", ""))
        return

    log("❓ No form and no email found; moving on")

# --- helpers ---

def _shot(page: Page, path: Path):
    try:
        page.screenshot(path=str(path), full_page=False)
        log(f"Screenshot saved: {path}")
    except Exception as e:
        log(f"Screenshot failed: {e}")

def _try_fill(page: Page, selector: str, value: str, label: str):
    if not value:
        return
    try:
        page.fill(selector, value)
        log(f"Filled {label}")
    except Exception as e:
        log(f"{label.capitalize()} not filled: {e}")

def _apply_fill(page: Page, plan_selector: str, value: str, which: str):
    """
    plan_selector is encoded as: FORM>>{form_index}>>EL#{i}[::select::{key}] or ::check
    We resolve it back to the element and apply the right action.
    """
    if value in (None, ""):
        return
    try:
        parts = plan_selector.split(">>")
        form_index = int(parts[1])
        rest = parts[2]  # EL#{i}[::select::{key}] etc.
        el_index = int(rest.split("#")[1].split(":")[0])
        form = page.locator("form").nth(form_index)
        el = form.locator("input:not([type=hidden]), textarea, select").nth(el_index)

        if "::check" in rest:
            try:
                checked = el.is_checked()
            except Exception:
                checked = False
            if not checked:
                el.check(timeout=1500)
                log(f"Checked: {which}")
            return

        if "::select::" in rest:
            # try match by option text or value
            try:
                el.select_option(label=value)
            except Exception:
                try:
                    el.select_option(value=value)
                except Exception:
                    pass
            log(f"Selected {which}: {value}")
            return

        # default: fill
        el.fill(str(value))
        log(f"Filled {which}")
    except Exception as e:
        log(f"Could not apply fill for {which}: {e}")

def _enqueue_emails(url: str, recipients: List[str], message: str):
    """
    Placeholder: push to your email pipeline / DB.
    Wire this to your real send/queue logic (e.g., FastAPI endpoint or Celery task).
    """
    try:
        log(f"Queued emails -> {recipients} | site={url} | body_len={len(message or '')}")
    except Exception as e:
        log(f"Failed to enqueue emails: {e}")

def _detect_submission_outcome(page: Page, form_index: int) -> Tuple[str, str]:
    """
    Returns ("success"|"failed", reason_if_failed).
    Strict: only success if explicit success text is found.
    """
    success_keywords = [
        "thank you", "thanks for your", "message sent", "form submitted",
        "successfully sent", "we have received", "submission complete",
        "your message has been received", "we'll be in touch", "we will contact you"
    ]
    error_keywords = [
        "validation errors", "please confirm the fields", "please correct the highlighted",
        "please fix the following", "required field", "this field is required", "invalid",
        "captcha", "try again", "error", "failed", "not sent", "unable to send", "something went wrong"
    ]
    def _txt(loc) -> str:
        try:
            return (loc.inner_text(timeout=1500) or "").lower()
        except Exception:
            return ""

    # Prefer text near the submitted form
    form_text = ""
    try:
        form_text = _txt(page.locator("form").nth(form_index))
    except Exception:
        pass
    try:
        body_text = (page.evaluate("() => document.body?.innerText || ''") or "").lower()
    except Exception:
        body_text = ""

    scopes = [t for t in [form_text, body_text] if t]

    for s in scopes:
        if any(kw in s for kw in success_keywords):
            return "success", ""
    for s in scopes:
        for ek in error_keywords:
            if ek in s:
                return "failed", ek
    return "failed", ""
