from __future__ import annotations

import sys
import os
import asyncio
import subprocess
from typing import Tuple, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Error as PWError
from app.log_stream import log

# ---------- Windows event-loop policy helpers ----------

def _force_windows_proactor(force: bool = True) -> None:
    """Ensure the Windows event loop policy supports subprocesses."""
    if not sys.platform.startswith("win"):
        return
    try:
        pro = getattr(asyncio, "WindowsProactorEventLoopPolicy", None)
        if pro:
            asyncio.set_event_loop_policy(pro())
            log("Event loop policy set to WindowsProactorEventLoopPolicy")
    except Exception as e:
        log(f"Warning: could not set Proactor event loop policy: {e}")

# ---------- Optional: auto-install browser if missing ----------

def _install_browser_if_needed(name: str = "firefox") -> None:
    """If launching complains browser is not installed, try to install it."""
    try:
        log(f"Attempting playwright install {name}…")
        subprocess.run([sys.executable, "-m", "playwright", "install", name], check=True)
        log(f"Playwright {name} installed")
    except Exception as e:
        log(f"Could not auto-install {name}: {e}")

def _compute_headless(explicit: Optional[bool]) -> bool:
    """Default headless=True unless user explicitly wants headful or PWDEBUG/HEADFUL is set."""
    if explicit is not None:
        return explicit
    if os.getenv("PWDEBUG") or os.getenv("HEADFUL") == "1":
        return False
    return True

def launch_browser(
    proxy: str = "",
    headless: Optional[bool] = None,
    browser_name: str = "firefox",
    viewport: Optional[tuple[int, int]] = (1366, 900),
) -> Tuple[BrowserContext, Page, Browser, any]:
    """
    Start Playwright and open a single page.
    Returns: (context, page, browser, playwright_handle)
    """
    _force_windows_proactor(force=True)

    # Start Playwright
    try:
        p = sync_playwright().start()
    except NotImplementedError:
        _force_windows_proactor(force=True)
        p = sync_playwright().start()

    # Select launcher
    launcher = {
        "firefox": p.firefox,
        "chromium": p.chromium,
        "webkit": p.webkit,
    }.get((browser_name or "firefox").lower(), p.firefox)

    # Build launch args
    resolved_headless = _compute_headless(headless)
    launch_kwargs = {
        "headless": resolved_headless,
        "timeout": 30000,
    }
    # Optional slow-mo when debugging
    try:
        slowmo = int(os.getenv("SLOWMO_MS", "0"))
        if slowmo > 0:
            launch_kwargs["slow_mo"] = slowmo
    except Exception:
        pass

    # DevTools for Chromium when headed
    if launcher is p.chromium and not resolved_headless and os.getenv("DEVTOOLS") == "1":
        launch_kwargs["devtools"] = True

    if proxy:
        launch_kwargs["proxy"] = {"server": proxy}

    # Launch
    try:
        browser = launcher.launch(**launch_kwargs)
    except PWError as e:
        msg = str(e).lower()
        if "executable doesn't exist" in msg or "browser is not downloaded" in msg:
            _install_browser_if_needed((browser_name or "firefox").lower())
            browser = launcher.launch(**launch_kwargs)
        else:
            raise

    # Context & page
    context_kwargs = {}
    if viewport:
        context_kwargs["viewport"] = {"width": viewport[0], "height": viewport[1]}
    context = browser.new_context(**context_kwargs)
    page = context.new_page()

    # Defaults
    try:
        page.set_default_timeout(45000)
        page.set_default_navigation_timeout(45000)
    except Exception:
        pass

    log(f"Browser launched: {(browser_name or 'firefox').lower()} | headless={resolved_headless} | proxy={'yes' if proxy else 'no'}")
    return context, page, browser, p


def close_browser(context: BrowserContext, browser: Browser, p: any) -> None:
    """Close page/context/browser and stop Playwright. Safe to call partially initialized."""
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
        if p:
            p.stop()
    except Exception:
        pass
