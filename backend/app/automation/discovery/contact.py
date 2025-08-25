# backend/app/automation/contact_finder.py
from __future__ import annotations

from typing import Dict
from urllib.parse import urlparse, urlunparse
from playwright.sync_api import Page
from app.log_stream import log
from app.automation.io.email import extract_emails_from_text
from app.automation.discovery.form import detect_contact_form

CONTACT_SEGMENTS = ("contact", "contact-us", "contactus", "support", "help")
COMMON_CONTACT_PATHS = (
    "/contact", "/contact-us", "/contactus",
    "/support", "/support/contact", "/company/contact"
)

EXCLUDE_HREF_PREFIX = ("#", "javascript:", "tel:", "mailto:")
EXCLUDE_HOST_PARTS = (
    "facebook.com", "twitter.com", "x.com", "linkedin.com", "instagram.com",
    "youtu.be", "youtube.com", "maps.google.", "goo.gl/maps"
)

def _origin(url: str) -> str:
    u = urlparse(url)
    return urlunparse((u.scheme or "http", u.netloc, "", "", "", ""))

def _is_contact_href(href: str) -> bool:
    if not href:
        return False
    h = href.strip().lower()
    if h.startswith(EXCLUDE_HREF_PREFIX):
        return False
    try:
        host = urlparse(h).netloc.lower()
    except Exception:
        host = ""
    if any(x in host for x in EXCLUDE_HOST_PARTS):
        return False
    path = urlparse(h).path.lower()
    return any(seg in path for seg in CONTACT_SEGMENTS)

def _try_click_contact_link(page: Page) -> bool:
    # Click anchors with hrefs that *really* look like contact/support.
    try:
        links = page.locator("a[href]")
        count = links.count()
    except Exception:
        count = 0

    for i in range(min(count, 200)):  # cap for very large pages
        try:
            a = links.nth(i)
            href = a.get_attribute("href") or ""
            if not _is_contact_href(href):
                continue
            if not a.is_visible(timeout=400):
                continue
            a.scroll_into_view_if_needed(timeout=800)
            a.click(timeout=1500)
            page.wait_for_load_state("domcontentloaded", timeout=8000)
            log(f'Navigated via anchor href="{href}"')
            return True
        except Exception:
            continue
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
    Deterministic discovery:
      1) collect emails on current page
      2) click only *real* contact/support hrefs
      3) try a few common paths on same origin
      4) detect form on resulting page
    """
    start_url = page.url
    base = _origin(start_url)

    emails_here = _extract_page_emails(page)
    changed = _try_click_contact_link(page)
    if not changed:
        changed = _try_common_paths(page, base)

    emails_after = _extract_page_emails(page)
    form_info = detect_contact_form(page)

    return {
        "page_changed": changed,
        "url": page.url,
        "emails": emails_after or emails_here,
        "form": form_info,
    }
