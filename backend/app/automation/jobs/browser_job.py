# backend/app/automation/browser_engine.py
from playwright.sync_api import sync_playwright
import sys, asyncio
from app.log_stream import log

def _ensure_windows_proactor():
    """On Windows, make sure the event loop policy supports subprocesses."""
    if not sys.platform.startswith("win"):
        return
    try:
        sel = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
        pro = getattr(asyncio, "WindowsProactorEventLoopPolicy", None)
        if sel and pro:
            policy = asyncio.get_event_loop_policy()
            if isinstance(policy, sel):
                asyncio.set_event_loop_policy(pro())
                log("Switched event loop policy to WindowsProactorEventLoopPolicy for Playwright")
    except Exception as e:
        log(f"Warning: could not switch event loop policy: {e}")

def launch_browser(proxy: str = ""):
    _ensure_windows_proactor()   # <-- add this line

    p = sync_playwright().start()
    # ... the rest of your existing code that launches the browser/context/page ...
    # return context, page, browser, p
