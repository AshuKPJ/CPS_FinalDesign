# backend/playwright_config.py
from pathlib import Path
from typing import Optional, Tuple
from playwright.sync_api import BrowserType, Playwright, Browser, BrowserContext, Page

# Defaults
BROWSER_NAME = "firefox"      # "chromium" | "firefox" | "webkit"
HEADLESS = False               # False => visible window
SLOW_MO = 250                  # ms delay between actions
CHANNEL = "None"             # only valid for chromium ("chrome" or "msedge" or None)

DEFAULT_NAVIGATION_TIMEOUT = 45_000  # ms
DEFAULT_TIMEOUT = 45_000             # ms

# Optional proxy (or set at runtime)
PROXY = None
# PROXY = {"server": "http://user:pass@host:port"}

# Artifacts
VIDEO_DIR = Path("run_artifacts/video")
SCREENSHOT_DIR = Path("run_artifacts/screenshots")
PROFILE_DIR = Path("run_artifacts/profile")   # used for persistent context
VIEWPORT = None  # None => real OS window; in headless use {"width":1366, "height":900}

CHROMIUM_ARGS = [
    "--start-maximized",
    "--window-position=100,100",
    # "--disable-gpu", "--use-angle=swiftshader",  # uncomment if RDP/VM issues
]


def launch_browser(
    playwright: Playwright,
    *,
    headless: Optional[bool] = None,
    proxy: Optional[dict] = None,
    slow_mo: Optional[int] = None,
) -> Tuple[Optional[Browser], BrowserContext, Page]:
    """
    Returns (browser, context, page).
    - If headless is False (or global HEADLESS is False), uses persistent context (visible window).
    - If headless is True, uses regular launch() + new_context() (headless).
    """
    # ensure folders exist
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    browser_name = BROWSER_NAME
    headless = HEADLESS if headless is None else headless
    slow_mo = SLOW_MO if slow_mo is None else slow_mo
    proxy = PROXY if proxy is None else proxy

    browser_type: BrowserType = getattr(playwright, browser_name)

    # Headed: persistent context (this is what worked for you)
    if not headless and browser_name == "chromium":
        launch_kw = {
            "user_data_dir": str(PROFILE_DIR.resolve()),
            "headless": False,
            "args": CHROMIUM_ARGS,
        }
        if slow_mo and slow_mo > 0:
            launch_kw["slow_mo"] = slow_mo
        if proxy:
            launch_kw["proxy"] = proxy
        if CHANNEL:
            launch_kw["channel"] = CHANNEL  # "chrome" or "msedge"

        context = playwright.chromium.launch_persistent_context(**launch_kw)
        page = context.new_page()
        context.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)
        context.set_default_timeout(DEFAULT_TIMEOUT)
        # In persistent mode there's no separate Browser object
        return None, context, page

    # Headless (or non-chromium headed): regular launch
    launch_args = {
        "headless": True if headless else False,
        "args": CHROMIUM_ARGS if browser_name == "chromium" else [],
    }
    if slow_mo and slow_mo > 0:
        launch_args["slow_mo"] = slow_mo
    if proxy:
        launch_args["proxy"] = proxy
    if browser_name == "chromium" and CHANNEL and not headless:
        # Headed but not persistent (e.g., firefox/webkit), CHANNEL only for chromium
        launch_args["channel"] = CHANNEL

    browser: Browser = browser_type.launch(**launch_args)
    context = browser.new_context(
        viewport=VIEWPORT if headless else None,  # real window size if headed
        record_video_dir=str(VIDEO_DIR),
    )
    context.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)
    context.set_default_timeout(DEFAULT_TIMEOUT)
    page = context.new_page()
    return browser, context, page
