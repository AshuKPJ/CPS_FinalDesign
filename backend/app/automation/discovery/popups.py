# backend/app/automation/popup_killer.py
from __future__ import annotations

import re
from typing import Iterable
from urllib.parse import urlparse
from playwright.sync_api import BrowserContext, Page, Frame
from app.log_stream import log

# Recognized cookie/consent providers (CMPs). If an iframe URL host matches
# one of these, it is safe to click "Accept" inside the frame.
CMP_HOST_PATTERNS = (
    "cookielaw.org",     # OneTrust
    "cookiebot.com",     # Cookiebot
    "cookieyes.com",     # CookieYes
    "trustarc.com",      # TrustArc
    "quantcast",         # Quantcast / TCF
    "didomi",            # Didomi
    "termly",            # Termly
)

# Consent/cookie containers. We ONLY click inside these or known CMP iframes.
CONSENT_CONTAINER = (
    "[id*='cookie' i], [class*='cookie' i], "
    "[id*='consent' i], [class*='consent' i]"
)

# Buttons that are *only* valid inside a consent UI
ACCEPT_BUTTONS = (
    "button[id*='accept' i], button[class*='accept' i]",
    "button[id*='agree'  i], button[class*='agree'  i]",
    "button[id*='allow'  i], button[class*='allow'  i]",
    "button[aria-label*='accept' i]",
    "button[title*='accept' i]",
)
ACCEPT_TEXT_PATTERNS = tuple(re.compile(p, re.I) for p in (
    r"^accept(\s+all)?$",
    r"^agree$",
    r"^allow(\s+all)?$",
    r"^i agree$",
    r"^ok$",
    r"^got it$",
    r"^continue$",
))

def _is_cmp_iframe(frame: Frame) -> bool:
    try:
        url = frame.url or ""
    except Exception:
        return False
    host = urlparse(url).netloc.lower()
    return any(p in host for p in CMP_HOST_PATTERNS)

def _click_first(frame: Frame, selector: str, label: str) -> bool:
    try:
        loc = frame.locator(selector)
        if loc.count() > 0 and loc.first.is_visible(timeout=600):
            loc.first.click(timeout=700)
            log(f"[popup] Clicked {label}: {selector}")
            return True
    except Exception:
        pass
    return False

def _click_text(frame: Frame, patterns: Iterable[re.Pattern], label: str) -> bool:
    for pat in patterns:
        # role-based first
        try:
            btn = frame.get_by_role("button", name=pat)
            if btn.count() > 0 and btn.first.is_visible(timeout=600):
                btn.first.click(timeout=700)
                log(f"[popup] Clicked {label} by role: {pat.pattern}")
                return True
        except Exception:
            pass
        # fallback: contains-text
        try:
            txt = pat.pattern.strip("^$")
            loc = frame.locator(f"button:has-text('{txt}')")
            if loc.count() > 0 and loc.first.is_visible(timeout=600):
                loc.first.click(timeout=700)
                log(f"[popup] Clicked {label} by text: {txt}")
                return True
        except Exception:
            pass
    return False

def _kill_in_frame(frame: Frame) -> int:
    """
    Click ONLY when we are sure it's a consent banner:
    - inside a known CMP iframe, or
    - inside an element whose id/class/aria mentions cookie/consent.
    """
    hits = 0

    # 1) Known CMP iframe: safe to click
    if _is_cmp_iframe(frame):
        for sel in ACCEPT_BUTTONS:
            if _click_first(frame, sel, "consent-accept"):
                return 1
        if _click_text(frame, ACCEPT_TEXT_PATTERNS, "consent-accept"):
            return 1
        return 0

    # 2) DOM consent container
    try:
        boxes = frame.locator(CONSENT_CONTAINER)
        count = boxes.count()
    except Exception:
        count = 0

    if count > 0:
        box = boxes.first
        for sel in ACCEPT_BUTTONS:
            try:
                inside = box.locator(sel)
                if inside.count() > 0 and inside.first.is_visible(timeout=600):
                    inside.first.click(timeout=700)
                    log(f"[popup] Clicked consent-accept in container: {sel}")
                    return 1
            except Exception:
                pass
        if _click_text(frame, ACCEPT_TEXT_PATTERNS, "consent-accept"):
            return 1

    # IMPORTANT: do NOT click generic "Close/OK/primary" outside consent UIs.
    return hits

def try_kill_popups(page: Page, passes: int = 2) -> int:
    """Best-effort, SAFE cookie/consent dismiss. Returns number of clicks."""
    total = 0
    for _ in range(passes):
        try:
            total += _kill_in_frame(page.main_frame)
            for fr in page.frames:
                if fr is not page.main_frame:
                    total += _kill_in_frame(fr)
        except Exception:
            pass
    if total:
        log(f"[popup] Dismissed {total} consent banner(s).")
    return total

def attach_popup_handlers(context: BrowserContext) -> None:
    """Attach non-invasive handlers (dialogs + initial popup sweep)."""
    try:
        for p in context.pages:
            p.on("dialog", lambda d: d.dismiss())
            try_kill_popups(p)
        context.on("page", lambda p: (p.on("dialog", lambda d: d.dismiss()), try_kill_popups(p)))
        log("[popup] SAFE handlers attached.")
    except Exception:
        pass
