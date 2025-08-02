# backend/app/automation/form_detector.py

from playwright.async_api import async_playwright
from typing import Dict, Optional
import asyncio


async def detect_form_on_page(url: str, proxy: Optional[str] = None) -> Dict:
    result = {
        "form_detected": False,
        "form_fields": [],
        "has_captcha": False,
        "contact_url": url,
    }

    try:
        async with async_playwright() as p:
            browser_args = ["--no-sandbox"]
            if proxy:
                browser_args.append(f"--proxy-server={proxy}")

            browser = await p.chromium.launch(headless=True, args=browser_args)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url, timeout=30000)
            
            # Find all forms
            forms = await page.query_selector_all("form")
            if forms:
                result["form_detected"] = True
                first_form = forms[0]
                inputs = await first_form.query_selector_all("input, textarea, select")

                for input_el in inputs:
                    tag = await input_el.get_property("tagName")
                    input_type = await input_el.get_attribute("type")
                    name = await input_el.get_attribute("name")
                    placeholder = await input_el.get_attribute("placeholder")
                    label = await input_el.evaluate("(el) => el.labels?.[0]?.innerText || ''")
                    
                    result["form_fields"].append({
                        "tag": (tag or "").lower(),
                        "type": input_type,
                        "name": name,
                        "placeholder": placeholder,
                        "label": label,
                    })

                    if input_type and "captcha" in input_type.lower():
                        result["has_captcha"] = True

            await browser.close()

    except Exception as e:
        result["error"] = str(e)

    return result


# # For local testing only
# if __name__ == "__main__":
#     test_url = "https://example.com/contact"
#     print(asyncio.run(detect_form_on_page(test_url)))
