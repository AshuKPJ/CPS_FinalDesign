# backend/app/automation/form_detector.py

from playwright.async_api import async_playwright

async def detect_form_on_page(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=20000)
            forms = await page.query_selector_all("form")
            form_data = []

            for form in forms:
                form_info = {
                    "action": await form.get_attribute("action"),
                    "method": await form.get_attribute("method"),
                    "fields": []
                }
                inputs = await form.query_selector_all("input, textarea, select")
                for input_elem in inputs:
                    name = await input_elem.get_attribute("name")
                    typ = await input_elem.get_attribute("type") or input_elem.evaluate("el => el.tagName")
                    form_info["fields"].append({"name": name, "type": typ})
                form_data.append(form_info)

            return {"forms": form_data, "status": "success" if form_data else "no_forms"}

        except Exception as e:
            return {"error": str(e), "status": "error"}

        finally:
            await browser.close()
