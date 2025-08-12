# backend/app/automation/browser_job.py

import os
import sys
import traceback
from typing import List
import asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

from app.log_stream import log


# ------------------------------ Windows Event Loop Fix ------------------------------

def _ensure_windows_proactor_policy():
    if sys.platform.startswith("win"):
        try:
            current = asyncio.get_event_loop_policy().__class__.__name__
            if current != "WindowsProactorEventLoopPolicy":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                log("Event loop policy set to WindowsProactorEventLoopPolicy")
            else:
                log("Event loop policy already WindowsProactorEventLoopPolicy")
        except Exception as e:
            log(f"Could not set WindowsProactorEventLoopPolicy: {e}")


# ------------------------------ Helpers ------------------------------

def _int_env(name: str, default: int) -> int:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return int(v)
    except Exception:
        return default


# ------------------------------ CSV Helpers ------------------------------

def read_csv_safely(path: str) -> pd.DataFrame:
    log("")
    log("----------------------------------------------")
    log("Step 1 - Reading CSV")
    log(f"CSV path: {path}")
    log("Trying encoding: utf-8-sig (strict)")
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig", encoding_errors="strict")
    except UnicodeDecodeError:
        log("utf-8-sig failed. Trying encoding: latin1 (replace)")
    except Exception as e:
        log(f"utf-8-sig attempt failed: {e}. Trying encoding: latin1 (replace)")

    try:
        return pd.read_csv(path, dtype=str, encoding="latin1", encoding_errors="replace")
    except Exception as e:
        log(f"latin1 failed: {e}. Trying encoding: cp1252 (replace)")

    try:
        return pd.read_csv(path, dtype=str, encoding="cp1252", encoding_errors="replace")
    except Exception as e:
        raise RuntimeError(f"Unable to read CSV with utf-8-sig/latin1/cp1252. Last error: {e}")


def extract_websites(df: pd.DataFrame) -> List[str]:
    log("")
    log("----------------------------------------------")
    log("Step 2 - Normalizing Data")
    df.columns = df.columns.str.strip()
    log(f"Headers: {list(df.columns)}")

    if "website" not in df.columns:
        log("'website' column not found in CSV.")
        return []

    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    log("String columns trimmed.")

    log("")
    log("----------------------------------------------")
    log("Step 3 - Extracting Websites")
    websites = (
        df["website"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"": None})
        .dropna()
        .unique()
        .tolist()
    )
    log(f"Unique websites found: {len(websites)}")
    return websites


# ------------------------------ Core Job ------------------------------

def run(csv_path: str, proxy: str = "", halt_on_captcha: bool = True) -> None:
    try:
        log("")
        log("==============================================")
        log("Starting browser automation job")
        log("==============================================")

        _ensure_windows_proactor_policy()

        # single source of truth for timeouts
        nav_timeout = _int_env("NAV_TIMEOUT_MS", 45000)

        # artifacts
        artifacts_root = Path("run_artifacts")
        profile_dir     = artifacts_root / "profile"      # persistent profile for chromium
        screenshots_dir = artifacts_root / "screenshots"
        profile_dir.mkdir(parents=True, exist_ok=True)
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # CSV -> websites
        df = read_csv_safely(csv_path)
        log(f"CSV read successfully. Shape: {df.shape}")
        websites = extract_websites(df)
        if not websites:
            log("No valid websites to process. Exiting.")
            return

        # ----------------------------------------------
        # Step 4 - Launching Browser
        # ----------------------------------------------
        log("")
        log("----------------------------------------------")
        log("Step 4 - Launching Browser")
        log(f"Config - NAV_TIMEOUT_MS={nav_timeout}")
        if proxy:
            log(f"Config - PROXY={proxy}")

        # Choose engine via env: BROWSER_NAME=chromium|firefox|webkit (default chromium)
        browser_name = os.getenv("BROWSER_NAME", "firefox").strip().lower()
        log(f"Browser engine: {browser_name}")

        try:
            with sync_playwright() as p:
                chromium_args = ["--start-maximized", "--window-position=100,100"]

                # ---------- Chromium (visible) uses persistent context ----------
                if browser_name == "chromium":
                    launch_kw = {
                        "user_data_dir": str(profile_dir.resolve()),
                        "headless": False,           # visible window
                        "args": chromium_args,
                    }
                    if proxy:
                        launch_kw["proxy"] = {"server": proxy}
                    try:
                        launch_kw["channel"] = "chrome"  # prefer system Chrome if available
                        log("Launch channel: chrome (system Chrome)")
                    except Exception:
                        pass

                    log("Launching Chromium persistent context (visible window)...")
                    context = p.chromium.launch_persistent_context(**launch_kw)
                    log("Persistent context launched.")
                    page = context.new_page()

                # ---------- Firefox (visible) ----------
                elif browser_name == "firefox":
                    log("Launching Firefox...")
                    launch_kw = {"headless": False}
                    if proxy:
                        launch_kw["proxy"] = {"server": proxy}
                    browser = p.firefox.launch(**launch_kw)
                    log("Firefox launched.")
                    context = browser.new_context(viewport=None)  # real OS window
                    page = context.new_page()

                # ---------- WebKit (visible) ----------
                elif browser_name == "webkit":
                    log("Launching WebKit...")
                    launch_kw = {"headless": False}
                    if proxy:
                        launch_kw["proxy"] = {"server": proxy}
                    browser = p.webkit.launch(**launch_kw)
                    log("WebKit launched.")
                    context = browser.new_context(viewport=None)
                    page = context.new_page()

                else:
                    raise ValueError(f"Unsupported BROWSER_NAME: {browser_name}")

                # Timeouts and window sizing
                context.set_default_navigation_timeout(nav_timeout)
                context.set_default_timeout(nav_timeout)
                log("New page opened.")
                try:
                    page.evaluate("window.moveTo(0,0); window.resizeTo(screen.width, screen.height);")
                except Exception:
                    pass

                # ----------------------------------------------
                # Step 5 - Processing Websites
                # ----------------------------------------------
                total = len(websites)
                log("----------------------------------------------")
                log(f"Step 5 - Processing Websites (total: {total})")
                
                for idx, raw_url in enumerate(websites, start=1):
                    url = raw_url if raw_url.startswith(("http://", "https://")) else f"http://{raw_url}"
                    log("----------------------------------------------")
                    log(f"[{idx}/{total}] Target URL: {url}")
                
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    base = f"row{idx}_{ts}"
                
                    try:
                        loaded = False
                
                        # try primary URL
                        log("Navigating (attempt 1)")
                        try:
                            page.goto(url, timeout=nav_timeout, wait_until="domcontentloaded")
                            loaded = True
                            log(f"Loaded: {page.url}")
                        except Exception as e1:
                            log(f"First navigation failed: {e1}")
                
                            # If it was plain http, retry with https
                            if url.startswith("http://"):
                                https_url = "https://" + url[len("http://"):]
                                log(f"Retry with HTTPS: {https_url}")
                                try:
                                    page.goto(https_url, timeout=nav_timeout, wait_until="domcontentloaded")
                                    loaded = True
                                    log(f"Loaded: {page.url}")
                                except Exception as e2:
                                    log(f"HTTPS retry failed: {e2}")
                
                        if not loaded:
                            # save an error screenshot and continue to next URL
                            fail_shot = screenshots_dir / f"{base}_error.png"
                            try:
                                page.screenshot(path=str(fail_shot), full_page=False)
                                log(f"Error screenshot saved: {fail_shot}")
                            except Exception:
                                pass
                            
                            log(f"Skipping {url} after failed navigation. Moving to next URL.")
                            continue
                        
                        # Save a loaded screenshot
                        shot_path = screenshots_dir / f"{base}_loaded.png"
                        try:
                            page.screenshot(path=str(shot_path), full_page=False)
                            log(f"Screenshot saved: {shot_path}")
                        except Exception as e:
                            log(f"Screenshot failed: {e}")
                
                        # Count forms
                        form_count = page.locator("form").count()
                        log(f"Forms found: {form_count}")
                
                        if form_count > 0:
                            log("Filling basic fields")
                            try:
                                page.fill('input[name*="name"]', "John Doe")
                                log("Filled name")
                            except Exception as e:
                                log(f"Name not filled: {e}")
                
                            try:
                                page.fill('input[type="email"]', "john@example.com")
                                log("Filled email")
                            except Exception as e:
                                log(f"Email not filled: {e}")
                
                            try:
                                page.fill('textarea', "Hello from automation")
                                log("Filled message")
                            except Exception as e:
                                log(f"Message not filled: {e}")
                
                            try:
                                page.locator("form").first.locator(
                                    'button[type="submit"], input[type="submit"]'
                                ).first.click()
                                log("Submit attempted")
                            except Exception as e:
                                log(f"Submit not possible: {e}")
                        else:
                            log("No form on page")
                
                    except Exception as e:
                        # Decide whether to halt for likely CAPTCHAs; otherwise continue
                        err = str(e).lower()
                        is_captcha = any(k in err for k in ("captcha", "recaptcha", "hcaptcha"))
                        if is_captcha and halt_on_captcha:
                            log("Possible CAPTCHA encountered; halting because halt_on_captcha=True")
                            break
                        
                        fail_shot = screenshots_dir / f"{base}_error.png"
                        try:
                            page.screenshot(path=str(fail_shot), full_page=False)
                            log(f"Error screenshot saved: {fail_shot}")
                        except Exception:
                            pass
                        
                        log(f"Unhandled error for {url}: {e}. Continuing to next URL.")
                        continue
                    
                log("----------------------------------------------")
                log("Step 5 - Done")
                

                # ----------------------------------------------
                # Step 6 - Closing Browser
                # ----------------------------------------------
                log("")
                log("----------------------------------------------")
                log("Step 6 - Closing Browser")
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    # Only exists for firefox/webkit path
                    if 'browser' in locals() and browser:
                        browser.close()
                except Exception:
                    pass
                log("Browser closed.")

        except Exception:
            log("")
            log("==============================================")
            log("Critical error in Step 4 - Launching Browser")
            log("----------------------------------------------")
            log(traceback.format_exc())
            log("==============================================")
            return

    except Exception:
        log("")
        log("==============================================")
        log("Critical error in automation")
        log("----------------------------------------------")
        log(traceback.format_exc())
        log("==============================================")


# ------------------------------ Public Entry ------------------------------

def process_csv_and_submit(csv_path: str, proxy: str = "", halt_on_captcha: bool = True):
    run(csv_path, proxy, halt_on_captcha)


# ------------------------------ CLI Support ------------------------------

if __name__ == "__main__":
    # Example direct run:
    #   BROWSER_NAME=firefox python backend/app/automation/browser_job.py uploads/websites.csv "" true
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else "uploads/websites.csv"
    proxy_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    halt_arg = (sys.argv[3].lower() == "true") if len(sys.argv) > 3 else True
    process_csv_and_submit(csv_arg, proxy_arg, halt_arg)
