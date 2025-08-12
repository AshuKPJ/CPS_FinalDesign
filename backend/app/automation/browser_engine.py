# backend/app/automation/browser_engine.py

from typing import Tuple, Optional
from playwright.sync_api import sync_playwright, BrowserContext, Page
from app.log_stream import log
from .config import NAV_TIMEOUT_MS, BROWSER_NAME
from .popup_killer import attach_popup_handlers

def launch_browser(proxy: str = "") -> Tuple[Optional[BrowserContext], Optional[Page], Optional[object], object]:
    """
    Returns (context, page, browser, playwright)
    - For chromium persistent context, browser is None (context manages lifecycle)
    - For firefox/webkit, context created from browser
    """
    p = sync_playwright().start()
    chromium_args = ["--start-maximized", "--window-position=100,100"]

    if BROWSER_NAME == "chromium":
        log("Launching Chromium persistent context (visible window)...")
        launch_kw = {
            "user_data_dir": "run_artifacts/profile",
            "headless": False,
            "args": chromium_args,
        }
        if proxy:
            launch_kw["proxy"] = {"server": proxy}
        try:
            launch_kw["channel"] = "chrome"  # prefer system Chrome if available
            log("Launch channel: chrome (system Chrome)")
        except Exception:
            pass

        context = p.chromium.launch_persistent_context(**launch_kw)
        context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        context.set_default_timeout(NAV_TIMEOUT_MS)

        # 🔗 Attach popup/dialog handlers early
        try:
            attach_popup_handlers(context)
        except Exception:
            pass

        page = context.new_page()
        try:
            page.evaluate("window.moveTo(0,0); window.resizeTo(screen.width, screen.height);")
        except Exception:
            pass
        log("Chromium context ready.")
        return context, page, None, p

    elif BROWSER_NAME == "firefox":
        log("Launching Firefox...")
        kw = {"headless": False}
        if proxy:
            kw["proxy"] = {"server": proxy}
        browser = p.firefox.launch(**kw)
        context = browser.new_context(viewport=None)
        context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        context.set_default_timeout(NAV_TIMEOUT_MS)

        # 🔗 Attach popup/dialog handlers
        try:
            attach_popup_handlers(context)
        except Exception:
            pass

        page = context.new_page()
        log("Firefox context ready.")
        return context, page, browser, p

    elif BROWSER_NAME == "webkit":
        log("Launching WebKit...")
        kw = {"headless": False}
        if proxy:
            kw["proxy"] = {"server": proxy}
        browser = p.webkit.launch(**kw)
        context = browser.new_context(viewport=None)
        context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        context.set_default_timeout(NAV_TIMEOUT_MS)

        # 🔗 Attach popup/dialog handlers
        try:
            attach_popup_handlers(context)
        except Exception:
            pass

        page = context.new_page()
        log("WebKit context ready.")
        return context, page, browser, p

    else:
        p.stop()
        raise ValueError(f"Unsupported BROWSER_NAME: {BROWSER_NAME}")

def close_browser(context: Optional[BrowserContext], browser: Optional[object], p: object):
    from app.log_stream import log
    log("")
    log("----------------------------------------------")
    log("Step 6 - Closing Browser")
    try:
        if context:
            context.close()
    except Exception:
        pass
    try:
        if browser:
            browser.close()
    except Exception:
        pass
    try:
        p.stop()
    except Exception:
        pass
    log("Browser closed.")
