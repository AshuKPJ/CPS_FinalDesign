import asyncio
from playwright.async_api import async_playwright
from typing import Dict, Any

# A more robust implementation would use more sophisticated heuristics
# to find form elements. This is a functional starting point.
async def find_and_submit_form(url: str, user_data: Dict[str, Any], message: str) -> Dict[str, Any]:
    """
    Navigates to a URL, finds a contact form, fills it, and submits.
    """
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Simple heuristic to find form fields
            await page.locator('input[name*="name"], input[id*="name"]').first.fill(f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}")
            await page.locator('input[name*="email"], input[id*="email"]').first.fill(user_data.get('email', ''))
            await page.locator('textarea[name*="message"], textarea[id*="message"]').first.fill(message)
            
            # Simple heuristic for submit button
            await page.locator('button[type="submit"], input[type="submit"]').first.click()

            # Wait for navigation or a success message (highly site-specific)
            # This part would need significant improvement for real-world use.
            await page.wait_for_timeout(3000) 

            await browser.close()
            return {"status": "success", "details": f"Form submitted on {url}"}

        except Exception as e:
            await browser.close()
            return {"status": "submission_failed", "details": f"Error on {url}: {str(e)}"}