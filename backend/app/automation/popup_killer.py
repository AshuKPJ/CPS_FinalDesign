# backend/app/automation/popup_killer.py
from typing import Optional, Iterable
from playwright.sync_api import Page, BrowserContext, Frame
from app.log_stream import log

CLOSE_SELECTORS = [
    # roles/aria
    '[aria-label*="close" i]', '[role="button"][aria-label*="close" i]',
    # common libs
    '.mfp-close', '.fancybox-button--close', '.fancybox-close-small',
    '.modal .btn-close', '.modal .close', '.modal.show .btn-close', '.modal.show .close',
    '.pum-close', '.pum-active .pum-close', '.pum-overlay .pum-close',
    '.lepopup-close', '.sgpb-popup-close-button', '.sgpb-close', '.popmake-close',
    '.mc-closeModal', '.mc-modal .close', '#mc_embed_signup .close',
    # generic classes/ids
    '.popup-close', '.overlay-close', '.lightbox-close', '.close', '.close-btn', '#close', '#dismiss',
    # text / glyph “X” variants
    'button:has-text("×")', 'button:has-text("✕")', 'button:has-text("✖")', 'button:has-text("X")',
    'a:has-text("×")', 'a:has-text("✕")', 'a:has-text("✖")', 'a:has-text("X")',
    'text=/^\\s*[×✕✖X]\\s*$/',
    # common consent/buttons
    'button:has-text("Close")', 'button:has-text("Dismiss")',
    'button:has-text("No thanks")', 'button:has-text("No Thanks")',
]

COOKIE_ACCEPT_SELECTORS = [
    'button:has-text("Accept all")', 'button:has-text("Allow all")', 'button:has-text("Accept")',
    'button:has-text("I agree")', '#onetrust-accept-btn-handler', '.truste-button2', '.cc-allow',
]

def attach_popup_handlers(context: BrowserContext):
    def _on_page(page: Page):
        try:
            page.on("dialog", lambda d: (d.accept(), log(f"Dialog accepted: {d.type} - {d.message}")))
        except Exception:
            pass
    try:
        for p in context.pages:
            _on_page(p)
        context.on("page", lambda new_page: (_on_page(new_page), log("New popup page handler attached")))
    except Exception:
        pass

def close_new_popup_pages(context: BrowserContext):
    try:
        pages = context.pages
        if len(pages) <= 1:
            return
        for p in pages[1:]:
            try:
                url = p.url
            except Exception:
                url = "(unavailable)"
            try:
                p.close()
                log(f"Closed extra popup page: {url}")
            except Exception as e:
                log(f"Could not close extra page {url}: {e}")
    except Exception:
        pass

def _force_click(loc):
    try:
        # sometimes click needs JS dispatch (overlay covering etc.)
        loc.scroll_into_view_if_needed(timeout=500)
        loc.click(timeout=800)
        return True
    except Exception:
        try:
            box = loc.bounding_box()
            if box:
                loc.page.mouse.click(box["x"] + box["width"]/2, box["y"] + 5, delay=50)
                return True
        except Exception:
            return False
    return False

def _click_selectors_in(frame_like: Page | Frame, selectors: Iterable[str], label: str):
    for sel in selectors:
        try:
            loc = frame_like.locator(sel)
            count = loc.count()
            if count <= 0:
                continue
            lf = loc.first
            lf.wait_for(state="visible", timeout=600)
            if _force_click(lf):
                log(f'Clicked {label}: {sel}')
        except Exception:
            continue

def _nuke_overlays_in(frame_like: Page | Frame):
    try:
        removed = frame_like.evaluate("""
(() => {
  let removed = 0;
  const nodes = Array.from(document.querySelectorAll('div,section,aside,dialog'));
  for (const el of nodes) {
    const cs = getComputedStyle(el);
    const z = parseInt(cs.zIndex || '0', 10);
    const isFixed = cs.position === 'fixed';
    const big = el.offsetWidth >= innerWidth * 0.5 && el.offsetHeight >= innerHeight * 0.5;
    if (isFixed && big && z >= 999) { el.remove(); removed++; }
  }
  for (const el of [document.body, document.documentElement]) {
    if (el) { el.style.overflow = 'auto'; el.style.position = ''; }
  }
  return removed;
})()
        """)
        if removed:
            log(f"Removed {removed} large overlays")
    except Exception:
        pass

def _dismiss_in(frame_like: Page | Frame, accept_cookies: bool):
    try:
        frame_like.keyboard.press("Escape")
    except Exception:
        pass
    _click_selectors_in(frame_like, CLOSE_SELECTORS, "close")
    if accept_cookies:
        _click_selectors_in(frame_like, COOKIE_ACCEPT_SELECTORS, "cookie-accept")
    _nuke_overlays_in(frame_like)

def dismiss_popups(page: Page, context: Optional[BrowserContext] = None, accept_cookies: bool = True, retries: int = 2):
    if context:
        close_new_popup_pages(context)

    # main doc + iframes
    targets: list[Page | Frame] = [page] + page.frames
    for _ in range(max(1, retries)):
        for t in targets:
            _dismiss_in(t, accept_cookies)
