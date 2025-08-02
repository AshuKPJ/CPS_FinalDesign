# backend/app/automation/field_mapper.py

from typing import List, Dict
from playwright.async_api import Page

def normalize_label(label: str) -> str:
    return label.lower().strip().replace("_", " ").replace(":", "")

async def map_fields_and_fill(
    page: Page,
    form_selector: str,
    field_data: Dict[str, str]
):
    try:
        form = await page.query_selector(form_selector)
        if not form:
            return {"status": "form_not_found"}

        inputs = await form.query_selector_all("input, textarea, select")
        for input_elem in inputs:
            name = await input_elem.get_attribute("name")
            input_type = await input_elem.get_attribute("type") or "text"
            label_elem = await input_elem.evaluate_handle('el => el.labels ? el.labels[0]?.innerText : null')
            label = await label_elem.json_value() if label_elem else name

            matched_key = next(
                (key for key in field_data if normalize_label(key) in normalize_label(label or "") or normalize_label(label or "") in normalize_label(key)),
                None
            )

            if matched_key:
                value = field_data[matched_key]
                try:
                    if input_type in ["checkbox", "radio"]:
                        if value.lower() in ["yes", "true", "1"]:
                            await input_elem.check()
                    else:
                        await input_elem.fill(value)
                except Exception as fill_err:
                    print(f"Could not fill {matched_key}: {fill_err}")

        return {"status": "filled"}

    except Exception as e:
        return {"status": "error", "details": str(e)}
