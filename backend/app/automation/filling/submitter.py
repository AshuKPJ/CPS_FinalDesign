# backend/app/automation/filling/submitter.py
from __future__ import annotations

import re
import ipaddress
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

from playwright.sync_api import Page

from app.log_stream import log
from app.automation.discovery.popups import try_kill_popups
from app.automation.discovery.contact import find_contact_method
from app.automation.filling.mapping import build_fill_plan
from app.automation.core.config import NAV_TIMEOUT_MS, DBC_USER, DBC_PASS
from app.automation.captcha.dbc import solve_recaptcha_v2_token_sync


# ───────────────────────────── URL helpers ─────────────────────────────

def _timestamped_base(idx: int) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"row{idx}_{ts}"

_ZW_RE = re.compile(r"[\u200B-\u200D\uFEFF\u2060\u180E]")

def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except Exception:
        return False

def _host_looks_valid(host: str) -> bool:
    if not host:
        return False
    if host == "localhost" or _is_ip(host):
        return True
    return "." in host  # has a dot like example.com

def _sanitize_and_normalize_url(raw_url: str) -> Optional[str]:
    """
    Make a navigable base URL or return None if we can't.
    - strip BOM/ZWSP/whitespace/punctuation wrappers
    - repair common scheme typos (http//, https:/)
    - add http:// if missing
    - move lone host from path→netloc
    - IDNA encode host
    """
    if not raw_url:
        return None
    s = str(raw_url)

    # Remove BOM/zero-width and whitespace everywhere
    s = _ZW_RE.sub("", s.replace("\ufeff", ""))
    s = s.strip().strip('"\''"<>`()[]{}")
    s = s.replace("\u00A0", " ")          # nbsp → space
    s = re.sub(r"\s+", "", s)             # URLs cannot contain spaces

    if not s:
        return None

    # Repair very common scheme typos BEFORE checking for scheme
    s = re.sub(r"^(https?)//", r"\1://", s, flags=re.I)       # http//example → http://example
    s = re.sub(r"^(https?):/([^/])", r"\1://\2", s, flags=re.I)  # http:/example → http://example

    # If missing a scheme, add http://
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", s):
        s = "http://" + s

    # Normalize triple slashes like http:/// → http://
    s = s.replace(":///", "://")

    u = urllib.parse.urlparse(s)

    # If netloc is empty but path holds host, move it
    host = (u.netloc or "").strip()
    path = (u.path or "").strip()
    if not host and path:
        host = path
        path = ""
        u = u._replace(netloc=host, path=path)

    # Strip credentials if present
    if "@" in host:
        host = host.split("@", 1)[-1]

    host = host.rstrip(".")

    # IDNA encode hostname (keep :port)
    try:
        if ":" in host:
            h, port = host.rsplit(":", 1)
            host = f"{h.encode('idna').decode('ascii')}:{port}"
        else:
            host = host.encode("idna").decode("ascii")
    except Exception:
        pass

    if not _host_looks_valid(host):
        return None

    return urllib.parse.urlunparse((u.scheme.lower(), host, "", "", "", ""))

def _candidate_urls(clean_url: str) -> List[str]:
    """Generate smart variants: prefer https, then http, and toggle www."""
    out: List[str] = []
    u = urllib.parse.urlparse(clean_url)
    host = u.netloc

    # toggle www
    base_hosts = [host]
    if host.startswith("www."):
        base_hosts.append(host[4:])
    else:
        base_hosts.append("www." + host)

    # prefer https first
    for scheme in ("https", "http"):
        for h in base_hosts:
            url = urllib.parse.urlunparse((scheme, h, "", "", "", ""))
            if url not in out:
                out.append(url)
    return out


# ───────────────────────────── form helpers ─────────────────────────────

_DIGITS = re.compile(r"\D+")
def _digits(s: str) -> str: return _DIGITS.sub("", s or "")

def _format_phone_for_input(raw: str, pattern: Optional[str]) -> str:
    """
    Normalize phone text for common web inputs:
      - prefer last 10 digits
      - if input pattern looks digits-only → return bare digits
      - else return 999-999-9999 for 10 digits
    """
    d = _digits(raw)
    if not d:
        return ""
    if len(d) >= 10:
        d = d[-10:]
    if pattern and re.fullmatch(r"^\^?\\d[\d\-\(\)\s\+]*\$?$", pattern):
        return d
    if len(d) == 10:
        return f"{d[0:3]}-{d[3:6]}-{d[6:]}"
    return d

def _shot(page: Page, path: Path):
    try:
        page.screenshot(path=str(path), full_page=False)
        log(f"Screenshot saved: {path}")
        return str(path)  # return saved file path
    except Exception as e:
        log(f"Screenshot failed: {e}")
        return None

def _result(
    *,
    idx: int,
    input_url: str,
    page: Page | None,
    method: str,            # "form" | "email" | "none"
    status: str,            # "success" | "fail" | "email_only" | "skipped" | "nav_fail"
    reason: str = "",
    emails: Optional[List[str]] = None,
    shots: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    return {
        "idx": idx,
        "input_url": input_url,
        "final_url": (page.url if page else ""),
        "method": method,
        "status": status,
        "reason": reason,
        "emails": emails or [],
        "shots": shots or {},
    }

def _try_fill(page: Page, selector: str, value: Any, label: str):
    if value in (None, ""):
        return
    try:
        page.locator(selector).first.fill(str(value))
        log(f"Filled {label}")
    except Exception as e:
        log(f"{label.capitalize()} not filled: {e}")

def _apply_fill(page: Page, plan_selector: str, value: Any, which: str):
    """
    plan_selector from build_fill_plan:
      FORM>>{form_index}>>EL#{i}
      FORM>>{form_index}>>EL#{i}::select::{profile_key}
      FORM>>{form_index}>>EL#{i}::check
    """
    if value in (None, ""):
        return
    try:
        parts = plan_selector.split(">>")
        form_index = int(parts[1])
        rest = parts[2]  # e.g., "EL#3", "EL#5::select::country", "EL#7::check"
        el_index = int(rest.split("#")[1].split(":")[0])

        form = page.locator("form").nth(form_index)
        el = form.locator(
            "input:not([type=hidden]):not([name='g-recaptcha-response']):not(#g-recaptcha-response), "
            "textarea:not([name='g-recaptcha-response']):not(#g-recaptcha-response), "
            "select"
        ).nth(el_index)

        if "::check" in rest:
            try:
                if not el.is_checked():
                    el.check(timeout=1500)
            except Exception:
                try:
                    el.click(timeout=1500)
                except Exception:
                    pass
            log(f"Checked: {which}")
            return

        if "::select::" in rest:
            try:
                el.select_option(label=str(value))
            except Exception:
                try:
                    el.select_option(value=str(value))
                except Exception:
                    pass
            log(f"Selected {which}: {value}")
            return

        itype = (el.get_attribute("type") or "").lower()
        if "phone" in which or "phone_number" in which or itype == "tel":
            pat = el.get_attribute("pattern") or ""
            value = _format_phone_for_input(str(value), pat)
        el.fill(str(value))
        log(f"Filled {which}")
    except Exception as e:
        log(f"Could not apply fill for {which}: {e}")

def _newsletter_no_and_selects(form) -> None:
    """
    Choose 'No' for newsletter radios/selects; choose 'Other' for generic selects.
    Skip country/state-like selects.
    """
    # Radios 'No'
    try:
        group = form.locator(":is(fieldset,div,section):has-text('Subscribe'):has-text('Newsletter')").first
        target = group if group.count() else form
        no_label = target.locator("label:has-text('No')").first
        if no_label.count():
            no_label.click(timeout=1500)
        else:
            radio_no = target.locator("input[type='radio'][value*='no' i]:visible").first
            if radio_no.count():
                radio_no.check(timeout=1500)
    except Exception:
        pass

    # Selects: prefer "Other"; if newsletter select → pick "No"
    try:
        selects = form.locator("select:visible")
        for i in range(selects.count()):
            sel = selects.nth(i)
            try:
                label_txt = sel.evaluate("""(el)=>{
                  const id=el.id;
                  if(id){const lab=document.querySelector(`label[for="${id}"]`);return lab?lab.innerText:''}
                  return ''
                }""") or ""
            except Exception:
                label_txt = ""
            if re.search(r"\b(country|state|province|region|city|zip|postal)\b", label_txt, re.I):
                continue
            try:
                sel.select_option(label=re.compile(r"Other", re.I))
            except Exception:
                if re.search(r"(newsletter|subscribe)", label_txt, re.I):
                    try:
                        sel.select_option(label=re.compile(r"^No$", re.I))
                    except Exception:
                        pass
    except Exception:
        pass

def _has_recaptcha(form, page: Page) -> bool:
    try:
        if form.locator("#g-recaptcha, #recaptcha, [name='g-recaptcha-response'], #g-recaptcha-response").count():
            return True
    except Exception:
        pass
    try:
        if page.locator("iframe[src*='recaptcha']").count():
            return True
    except Exception:
        pass
    return False

def _try_click_recaptcha_checkbox(page: Page) -> bool:
    """Basic attempt for reCAPTCHA v2 checkbox (no external solver)."""
    try:
        fl = page.frame_locator("iframe[src*='recaptcha']").first
        if not fl.count():
            return False
        box = fl.locator("#recaptcha-anchor").first
        if not box.count():
            return False
        box.click(timeout=4000)
        log("Clicked reCAPTCHA checkbox")
        return True
    except Exception:
        return False

def _extract_recaptcha_sitekey(form, page: Page) -> Optional[str]:
    # 1) <div class="g-recaptcha" data-sitekey="...">
    try:
        key = form.locator("div.g-recaptcha").first.get_attribute("data-sitekey")
        if key:
            return key
    except Exception:
        pass
    # 2) <iframe src=".../recaptcha/api2/anchor?ar=1&k=<sitekey>&...">
    try:
        ifr = page.locator("iframe[src*='recaptcha']").first
        if ifr.count():
            src = ifr.get_attribute("src") or ""
            q = urllib.parse.urlparse(src).query
            params = urllib.parse.parse_qs(q)
            for k in ("k", "sitekey", "render"):
                if params.get(k):
                    return params[k][0]
    except Exception:
        pass
    return None

def _inject_recaptcha_token(page: Page, token: str) -> None:
    # Ensure the textarea exists and set the token
    js = """
    (tkn) => {
      let ta = document.getElementById('g-recaptcha-response') ||
               document.querySelector('textarea[name="g-recaptcha-response"]');
      if (!ta) {
        ta = document.createElement('textarea');
        ta.id = 'g-recaptcha-response';
        ta.name = 'g-recaptcha-response';
        ta.style.display = 'none';
        document.body.appendChild(ta);
      }
      ta.value = tkn;
      const evt = new Event('input', { bubbles: true });
      ta.dispatchEvent(evt);
    }
    """
    try:
        page.evaluate(js, token)
    except Exception:
        pass

def _enqueue_emails(url: str, recipients: List[str], message: str):
    """Placeholder: connect to your email pipeline if needed."""
    try:
        log(f"Queued emails -> {recipients} | site={url} | body_len={len(message or '')}")
    except Exception as e:
        log(f"Failed to enqueue emails: {e}")

def _detect_submission_outcome(page: Page, form_index: int) -> Tuple[str, str]:
    """
    Returns ("success"|"failed", reason_if_failed).
    Success only when explicit positive wording is seen.
    """
    success_keywords = [
        "thank you", "thanks for your", "message sent", "form submitted",
        "successfully sent", "we have received", "submission complete",
        "your message has been received", "we'll be in touch", "we will contact you",
    ]
    error_keywords = [
        "validation errors", "please confirm the fields", "please correct the highlighted",
        "please fix the following", "required field", "this field is required", "invalid",
        "captcha", "try again", "error", "failed", "not sent", "unable to send", "something went wrong",
    ]

    def _txt(loc) -> str:
        try:
            return (loc.inner_text(timeout=1500) or "").lower()
        except Exception:
            return ""

    try:
        form_text = _txt(page.locator("form").nth(form_index))
    except Exception:
        form_text = ""
    try:
        body_text = (page.evaluate("() => document.body?.innerText || ''") or "").lower()
    except Exception:
        body_text = ""

    scopes = [t for t in (form_text, body_text) if t]

    for s in scopes:
        if any(kw in s for kw in success_keywords):
            return "success", ""
    for s in scopes:
        for ek in error_keywords:
            if ek in s:
                return "failed", ek
    return "failed", ""


# ───────────────────────────── main entry ─────────────────────────────

def process_single_site(
    page: Page,
    raw_url: str,
    idx: int,
    screenshots_dir: Path,
    halt_on_captcha: bool,
    message: str,
    user_profile: Optional[Dict[str, Any]],
    use_captcha_solver: bool = False,   # opt-in token solver
) -> Dict[str, Any]:
    """
    Process one website:
      1) sanitize URL + try smart variants (https/http, toggle www)
      2) dismiss popups
      3) find contact method
      4) prefer contact form; otherwise collect emails
      5) attempt submit (with clear CAPTCHA policy) and detect success
    """
    # Merge profile + message (UI message wins)
    profile: Dict[str, Any] = dict(user_profile or {})
    if message and message.strip():
        profile["message"] = message.strip()

    base = _timestamped_base(idx)
    shots: Dict[str, str] = {}

    def save(name: str, filename: str):
        p = screenshots_dir / f"{base}_{filename}.png"
        sp = _shot(page, p)
        if sp:
            shots[name] = sp

    clean_url = _sanitize_and_normalize_url(raw_url)

    log("----------------------------------------------")
    log(f"[{idx}] Target URL: {raw_url}")

    if not clean_url:
        reason = "Invalid URL after sanitization (BOM/space/host)"
        log(f"Invalid URL → {raw_url!r} | {reason}")
        save("nav_fail", "nav_fail")
        return _result(idx=idx, input_url=str(raw_url), page=page, method="none",
                       status="nav_fail", reason=reason, emails=[], shots=shots)

    # 1) Navigate: try variants (https/http + toggle www)
    loaded = False
    last_err = None
    for attempt, url_try in enumerate(_candidate_urls(clean_url), 1):
        try:
            log(f"Navigating (attempt {attempt}): {url_try}")
            page.goto(url_try, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
            loaded = True
            log(f"Loaded: {page.url}")
            break
        except Exception as e:
            last_err = e
            log(f"Attempt {attempt} failed: {e}")

    if not loaded:
        save("nav_fail", "nav_fail")
        msg = f"Skipping {clean_url} after failed navigation. Last error: {last_err}"
        log(msg)
        return _result(idx=idx, input_url=clean_url, page=page, method="none",
                       status="nav_fail", reason=str(last_err or ""), emails=[], shots=shots)

    # 2) Clear popups on initial load
    try:
        try_kill_popups(page)
    except Exception:
        pass

    # 3) Discover contact method (may navigate) → then sweep popups again
    try:
        contact = find_contact_method(page)
        log(f"Contact discovery: {contact}")
    except Exception as e:
        contact = {"page_changed": False, "url": page.url, "emails": [], "form": {"has_form": False}}
        log(f"Contact discovery failed: {e}")

    if contact.get("page_changed"):
        try:
            try_kill_popups(page)
        except Exception:
            pass
        save("contact", "contact")

    # Baseline shot
    save("loaded", "loaded")

    # 4) PRIORITY: FORM FIRST → then EMAIL (top 2)
    form_info: Dict[str, Any] = (contact.get("form") or {})
    emails: List[str] = contact.get("emails") or []

    if form_info.get("has_form"):
        form_index = int(form_info.get("index", 0))
        log("📝 Contact form detected; building fill plan from profile")

        # Build a plan; if none, try minimal fallback
        try:
            plan = build_fill_plan(page, form_index, profile) or []
        except Exception as e:
            log(f"build_fill_plan failed: {e}")
            plan = []

        if not plan:
            log("No mapped fields from profile; trying minimal fallback (email + message)")
            _try_fill(page, 'form >> input[type="email" i]:visible', profile.get("email", ""), "email")
            _try_fill(page, "form >> textarea:visible", profile.get("message", ""), "message")
        else:
            for sel, val, label in plan:
                _apply_fill(page, sel, val, label)

        # Newsletter → No, Selects → Other (best effort)
        try:
            form = page.locator("form").nth(form_index)
            _newsletter_no_and_selects(form)
        except Exception:
            pass

        # CAPTCHA handling (pre-submit)
        form = page.locator("form").nth(form_index)
        if _has_recaptcha(form, page):
            log("reCAPTCHA detected on form")

            # Decide credentials: user-level first, then env fallback
            u_user = profile.get("captcha_username") or ""
            u_pass = profile.get("captcha_password") or ""
            env_user, env_pass = DBC_USER or "", DBC_PASS or ""
            have_creds = bool(u_user and u_pass) or bool(env_user and env_pass)

            if use_captcha_solver and have_creds:
                sitekey = _extract_recaptcha_sitekey(form, page)
                if sitekey:
                    user = u_user or env_user
                    pwd  = u_pass or env_pass
                    log(f"Attempting DBC token solve (sitekey={sitekey[:8]}..., url={page.url})")
                    token = solve_recaptcha_v2_token_sync(sitekey, page.url, user, pwd)
                    if token:
                        _inject_recaptcha_token(page, token)
                        log("✅ reCAPTCHA token injected")
                    else:
                        log("⚠️ Token solve failed")
                        if halt_on_captcha:
                            save("captcha", "captcha")
                            return _result(idx=idx, input_url=raw_url, page=page, method="form",
                                           status="fail", reason="captcha", emails=emails, shots=shots)
                else:
                    log("⚠️ Could not find sitekey for token solve")
                    if halt_on_captcha:
                        save("captcha", "captcha")
                        return _result(idx=idx, input_url=raw_url, page=page, method="form",
                                       status="fail", reason="captcha", emails=emails, shots=shots)
            else:
                # No solver → try checkbox once; if not clickable, fail fast (do NOT submit)
                clicked = _try_click_recaptcha_checkbox(page)
                if clicked:
                    log("Attempted checkbox, proceeding to submit")
                else:
                    note = "captcha (unsolved; solver disabled and checkbox not clickable)"
                    log(f"⚠️ {note}")
                    if halt_on_captcha:
                        save("captcha", "captcha")
                    return _result(idx=idx, input_url=raw_url, page=page, method="form",
                                   status="fail", reason="captcha", emails=emails, shots=shots)

        # One more popup sweep before submit
        try:
            try_kill_popups(page)
        except Exception:
            pass

        # Attempt submit
        submit = form.locator('button[type="submit" i], input[type="submit" i], button:not([type])').first
        try:
            try:
                with page.expect_navigation(timeout=8000):
                    submit.click()
                log("Form submitted (navigation observed)")
            except Exception:
                submit.click(timeout=2500)
                page.wait_for_timeout(4000)  # AJAX-style submits
                log("Form submitted (likely AJAX, no navigation)")
        except Exception as e:
            save("submit_error", "submit_error")
            reason = f"submit_click: {e}"
            log(f"❌ Submit click failed: {e}")
            return _result(idx=idx, input_url=raw_url, page=page, method="form",
                           status="fail", reason=reason, emails=emails, shots=shots)

        # Post-submit evidence & strict outcome
        save("postsubmit", "postsubmit")
        outcome, reason = _detect_submission_outcome(page, form_index)

        if outcome == "success":
            log("✅ Success message detected after form submission")
            return _result(idx=idx, input_url=raw_url, page=page, method="form",
                           status="success", reason="", emails=emails, shots=shots)
        else:
            if reason:
                log(f"❌ Form submission failed: {reason}")
            else:
                log("❌ Form submission failed: No success confirmation detected")
            return _result(idx=idx, input_url=raw_url, page=page, method="form",
                           status="fail", reason=reason or "", emails=emails, shots=shots)

    # No form → EMAIL path (top 2)
    if emails:
        top2 = emails[:2]
        log(f"📧 No form found. Will email top {len(top2)}: {top2}")
        _enqueue_emails(url=page.url, recipients=top2, message=profile.get("message", ""))
        return _result(idx=idx, input_url=raw_url, page=page, method="email",
                       status="email_only", reason="", emails=top2, shots=shots)

    log("❓ No form and no email found; moving on")
    return _result(idx=idx, input_url=raw_url, page=page, method="none",
                   status="skipped", reason="No form/email on page", emails=[], shots=shots)
