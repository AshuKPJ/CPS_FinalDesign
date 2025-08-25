import os
import sys
import traceback
import pandas as pd
from playwright.sync_api import sync_playwright

# -------- Console encoding safe setup --------
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def log(msg: str):
    """Safe logger without icons or symbols."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        safe = msg.encode("utf-8", errors="replace").decode("utf-8")
        print(safe, flush=True)

# -------- CSV reading with robust encoding fallback --------
def read_csv_safely(path: str) -> pd.DataFrame:
    log("Step 1: Attempting to read CSV file safely...")
    try:
        log("Trying UTF-8-SIG encoding...")
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig", encoding_errors="strict")
    except UnicodeDecodeError:
        log("UTF-8 decode failed. Retrying with latin1 (replace).")
    except Exception as e:
        log(f"UTF-8 attempt failed for another reason: {e}")

    try:
        log("Trying latin1 encoding...")
        return pd.read_csv(path, dtype=str, encoding="latin1", encoding_errors="replace")
    except Exception as e:
        log(f"latin1 fallback failed: {e}. Retrying with cp1252 (replace).")

    try:
        log("Trying cp1252 encoding...")
        return pd.read_csv(path, dtype=str, encoding="cp1252", encoding_errors="replace")
    except Exception as e:
        raise RuntimeError(f"Unable to read CSV with utf-8/latin1/cp1252. Last error: {e}")

def run(csv_path: str, proxy: str = "", halt_on_captcha: bool = True):
    try:
        log("Starting browser automation job...")

        # Step 1: Read CSV
        log(f"Reading CSV from path: {csv_path}")
        df = read_csv_safely(csv_path)
        log(f"CSV successfully read. Shape: {df.shape}")

        # Step 2: Clean headers & values
        log("Cleaning column headers...")
        df.columns = df.columns.str.strip()
        log(f"Headers after strip: {list(df.columns)}")

        log("Cleaning string values in DataFrame...")
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

        # Step 3: Validate 'website' column
        if "website" not in df.columns:
            log("'website' column not found in CSV.")
            return

        # Step 4: Prepare website list
        log("Extracting website list from CSV...")
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
        log(f"Found {len(websites)} unique websites.")

        if not websites:
            log("No valid websites found in the CSV. Exiting.")
            return

        # Step 5: Launch browser
        log("Launching Playwright browser...")
        with sync_playwright() as p:
            launch_args = {}
            if proxy:
                log(f"Using proxy: {proxy}")
                launch_args["proxy"] = {"server": proxy}

            browser = p.chromium.launch(headless=False, **launch_args)
            log("Browser launched successfully.")

            context = browser.new_context()
            log("Created new browser context.")

            page = context.new_page()
            log("Opened a new page in the browser.")

            # Step 6: Process each website
            for idx, raw_url in enumerate(websites, start=1):
                url = raw_url if raw_url.startswith(("http://", "https://")) else f"http://{raw_url}"
                log(f"Processing Row {idx}: {url}")

                try:
                    log("Attempting to load page...")
                    try:
                        page.goto(url, timeout=15000)
                        log(f"Successfully loaded: {page.url}")
                    except Exception as e:
                        log(f"Initial load failed: {e}")
                        if url.startswith("http://"):
                            https_url = "https://" + url[len("http://"):]
                            log(f"Retrying with HTTPS: {https_url}")
                            page.goto(https_url, timeout=15000)
                            log(f"Loaded via HTTPS: {page.url}")
                        else:
                            raise

                    # Step 7: Check forms
                    form_count = page.locator("form").count()
                    log(f"Found {form_count} form(s) on: {page.url}")

                    if form_count > 0:
                        log("Attempting to fill the form fields...")
                        try:
                            page.fill('input[name*="name"]', "John Doe")
                            log("Filled name field.")
                        except Exception as e:
                            log(f"Could not fill name: {e}")

                        try:
                            page.fill('input[type="email"]', "john@example.com")
                            log("Filled email field.")
                        except Exception as e:
                            log(f"Could not fill email: {e}")

                        try:
                            page.fill('textarea', "Hello from automation")
                            log("Filled message field.")
                        except Exception as e:
                            log(f"Could not fill message: {e}")

                        try:
                            page.locator("form").first.locator('button[type="submit"], input[type="submit"]').first.click()
                            log(f"Submitted form on: {page.url}")
                        except Exception as e:
                            log(f"Could not submit form: {e}")
                    else:
                        log(f"No contact form found at: {page.url}")

                except Exception as e:
                    log(f"Error processing {url}:\n{e}")
                    if halt_on_captcha:
                        log("Halting due to error and halt_on_captcha=True.")
                        break

            # Step 8: Close browser
            log("Closing browser...")
            browser.close()
            log("Automation finished for all sites.")

    except Exception:
        log("Critical error in automation:")
        log(traceback.format_exc())

if __name__ == "__main__":
    csv_path = sys.argv[1]
    proxy = sys.argv[2] if len(sys.argv) > 2 else ""
    halt = (sys.argv[3].lower() == "true") if len(sys.argv) > 3 else True
    run(csv_path, proxy, halt)
