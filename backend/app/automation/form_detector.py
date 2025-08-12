# backend/app/automation/form_detector.py


from typing import Dict, Any
from playwright.sync_api import Page

def detect_contact_form(page: Page) -> Dict[str, Any]:
    """
    Returns info about the first 'real' contact form, ignoring search/newsletter if possible.
    """
    try:
        forms = page.locator("form")
        n = forms.count()
    except Exception:
        n = 0

    if n == 0:
        return {"has_form": False}

    # pick the first form that looks like a contact form, not search
    for i in range(min(n, 5)):
        f = forms.nth(i)
        try:
            html = f.evaluate("el => el.outerHTML.toLowerCase()")
        except Exception:
            html = ""

        # quick heuristics
        looks_search = ("search" in html) and ("type=\"search\"" in html or "name=\"s\"" in html)
        looks_newsletter = ("newsletter" in html) and ("email" in html)
        has_textarea = "<textarea" in html
        has_submit = ("type=\"submit\"" in html) or ("role=\"button\"" in html) or ("<button" in html)

        if looks_search or (looks_newsletter and not has_textarea):
            continue

        if has_submit:
            return {
                "has_form": True,
                "index": i,
                "has_textarea": has_textarea,
                "has_submit": has_submit
            }

    # fallback
    return {"has_form": True, "index": 0, "has_textarea": False, "has_submit": True}
