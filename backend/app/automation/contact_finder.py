# backend/app/automation/contact_finder.py

from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, urlunparse
from playwright.sync_api import Page
from app.log_stream import log
from .email_utils import extract_emails_from_text
from .form_detector import detect_contact_form

CONTACT_TEXTS = [
    "contact", "contact us", "get in touch", "support", "help",
    "customer service", "customer care", "about us", "about & contact"
]

COMMON_CONTACT_PATHS = [
    "/contact", "/contact-us", "/contactus", "/contact-us/", "/contact-us.html",
    "/contact.html", "/about/contact", "/company/contact"
]

def _origin(url: str) -> str:
    u = urlparse(url)
    return urlunparse((u.scheme or "http", u.netloc, "", "", "", ""))

def _try_click_contact_link(page: Page) -> bool:
    # 1) text-based anchor search
    for txt in CONTACT_TEXTS:
        try:
            loc = page.locator(f'a:has-text("{txt}")')
            if loc.count() > 0:
                loc.first.scroll_into_view_if_needed(timeout=800)
                loc.first.click(timeout=1500)
                page.wait_for_load_state("domcontentloaded", timeout=8000)
                log(f'Navigated via contact link: "{txt}"')
                return True
        except Exception:
            continue

    # 2) href pattern
    try:
        loc = page.locator('a[href*="contact"]')
        if loc.count() > 0:
            loc.first.scroll_into_view_if_needed(timeout=800)
            loc.first.click(timeout=1500)
            page.wait_for_load_state("domcontentloaded", timeout=8000)
            log('Navigated via href*="contact" link')
            return True
    except Exception:
        pass

    return False

def _try_common_paths(page: Page, base: str) -> bool:
    for path in COMMON_CONTACT_PATHS:
        url = base.rstrip("/") + path
        try:
            resp = page.goto(url, timeout=12000, wait_until="domcontentloaded")
            ok = True if not resp else (200 <= (resp.status or 200) < 400)
            if ok:
                log(f"Opened common contact path: {url}")
                return True
        except Exception:
            continue
    return False

def _extract_page_emails(page: Page):
    emails = set()
    try:
        # mailto links
        mailtos = page.eval_on_selector_all(
            'a[href^="mailto:"]',
            "els => els.map(e => e.getAttribute('href'))"
        )
        for m in (mailtos or []):
            if not m:
                continue
            addr = m.split("mailto:", 1)[1].split("?", 1)[0]
            if addr:
                emails.add(addr.strip().lower())
    except Exception:
        pass

    try:
        text = page.evaluate("() => document.body ? document.body.innerText : ''")
        for e in extract_emails_from_text(text or ""):
            emails.add(e)
    except Exception:
        pass

    return sorted(emails)

def find_contact_method(page: Page) -> Dict:
    """
    Attempts (on current page) to discover contact method.
    May navigate to a contact page.
    Returns:
      {
        "page_changed": bool,
        "url": str,
        "emails": [..],
        "form": {has_form: bool, ...}
      }
    """
    start_url = page.url

    # 0) emails on current page
    emails_here = _extract_page_emails(page)
    if emails_here:
        log(f"Emails found on current page: {emails_here}")

    # 1) try actual "Contact" navigation
    changed = _try_click_contact_link(page)
    if not changed:
        # 2) try common paths
        base = _origin(start_url)
        changed = _try_common_paths(page, base)

    # Now evaluate contact info on the (possibly new) page
    emails = _extract_page_emails(page)
    form_info = detect_contact_form(page)

    return {
        "page_changed": changed,
        "url": page.url,
        "emails": emails if emails else emails_here,
        "form": form_info,
    }
