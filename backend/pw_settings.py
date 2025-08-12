# backend/pw_settings.py
from pathlib import Path
from typing import Optional, Tuple
from playwright.sync_api import Playwright, BrowserType, Browser, BrowserContext, Page

# launch defaults
BROWSER_NAME = "chromium"     # "chromium" | "firefox" | "webkit"
HEADLESS = False              # False => visible window
SLOW_MO = 250                 # ms delay
CHANNEL = "chrome"            # use system Chrome; only for chromium
PROXY = None                  # e.g. {"server": "http://user:pass@host:port"}

# timeouts
NAV_TIMEOUT_MS = 45_000
DEFAULT_TIMEOUT_MS = 45_000

# window / artifacts
VIEWPORT = None               # None => real OS window (headed)
VIDEO_DIR = Path("run_artifacts/video")
SCREENSHOT_DIR = Path("run_artifacts/screenshots")
PROFILE_DIR = Path("run_artifacts/profile")
CHROMIUM_ARGS = [
    "--start-maximized",
    "--window-position=100,100",
    # "--disable-gpu", "--use-angle=swiftshader",
]

def launch_with_settings(
    playwright: Playwright,
    *,
    headless: Optional[bool] = None,
    proxy: Optional[dict] = None,
    slow_mo: Optional[int] = None,
) -> Tuple[Optional[Browser], BrowserContext, Page]:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    browser_name = BROWSER_NAME
    headless = HEADLESS if headless is None else headless
    slow_mo = SLOW_MO if slow_mo is None else slow_mo
    proxy = PROXY if proxy is None else proxy

    browser_type: BrowserType = getattr(playwright, browser_name)

    if not headless and browser_name == "chromium":
        # Visible window path (persistent context)
        kw = {
            "user_data_dir": str(PROFILE_DIR.resolve()),
            "headless": False,
            "args": CHROMIUM_ARGS,
        }
        if slow_mo and slow_mo > 0:
            kw["slow_mo"] = slow_mo
        if proxy:
            kw["proxy"] = proxy
        if CHANNEL:
            kw["channel"] = CHANNEL

        context = playwright.chromium.launch_persistent_context(**kw)
        page = context.new_page()
        context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        context.set_default_timeout(DEFAULT_TIMEOUT_MS)
        return None, context, page

    # Headless (or non-chromium headed)
    kw = {
        "headless": True if headless else False,
        "args": CHROMIUM_ARGS if browser_name == "chromium" else [],
    }
    if slow_mo and slow_mo > 0:
        kw["slow_mo"] = slow_mo
    if proxy:
        kw["proxy"] = proxy
    if browser_name == "chromium" and CHANNEL and not headless:
        kw["channel"] = CHANNEL

    browser: Browser = browser_type.launch(**kw)
    context = browser.new_context(
        viewport=VIEWPORT if headless else None,
        record_video_dir=str(VIDEO_DIR),
    )
    context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
    context.set_default_timeout(DEFAULT_TIMEOUT_MS)
    page = context.new_page()
    return browser, context, page
