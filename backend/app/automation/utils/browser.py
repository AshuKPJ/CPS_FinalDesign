# backend/app/automation/browser_utils.py

from playwright.async_api import async_playwright, Browser, Page

async def launch_browser() -> Browser:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    return browser

async def open_page(browser: Browser, url: str) -> Page:
    page = await browser.new_page()
    await page.goto(url, timeout=20000)
    return page

async def close_browser(browser: Browser):
    await browser.close()
