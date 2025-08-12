# backend/app/automation/field_mapper.py

from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from playwright.sync_api import Page, Locator
from app.log_stream import log

# Map profile keys → tokens we’ll look for in input name/id/label/placeholder
PROFILE_TOKENS: Dict[str, List[str]] = {
    "first_name": ["first name", "firstname", "first_name", "given name", "givenname", "fname"],
    "last_name":  ["last name", "lastname", "last_name", "surname", "family name", "lname"],
    "company_name": ["company", "organization", "organisation", "business", "firm"],
    "job_title": ["job title", "title", "position", "role"],
    "email": ["email", "e-mail", "mail"],
    "phone_number": ["phone", "telephone", "tel", "mobile", "cell"],
    "website_url": ["website", "site", "url", "homepage"],
    "subject": ["subject", "topic"],
    "referral_source": ["referral", "how did you hear", "how you heard"],
    "message": ["message", "comments", "comment", "inquiry", "enquiry", "details", "question"],
    "preferred_contact": ["preferred contact", "contact method", "how contact"],
    "city": ["city", "town"],
    "state": ["state", "province", "region/state"],
    "country": ["country", "nation"],
    "zip_code": ["zip", "postal", "postcode"],
    "industry": ["industry", "sector"],
    "best_time_to_contact": ["best time", "preferred time", "contact time"],
    "budget_range": ["budget", "price range", "budget range"],
    "product_interest": ["interest", "product interest", "service interest"],
    "is_existing_customer": ["existing customer", "current customer", "already a customer"],
    "language": ["language", "preferred language"],
    "timezone": ["timezone", "time zone"],
    "linkedin_url": ["linkedin", "linkedin url", "linkedin profile"],
    "notes": ["notes", "note", "additional info", "additional information"],
    "form_custom_field_1": ["custom", "custom1", "custom field 1"],
    "form_custom_field_2": ["custom2", "custom field 2"],
    "form_custom_field_3": ["custom3", "custom field 3"],
    "contact_source": ["contact source", "source"],
    "preferred_language": ["preferred language"],
    "region": ["region"],
}

# Inputs we attempt to map and fill inside a given <form>
INPUT_SELECTOR = "input:not([type=hidden]):not([disabled]), textarea:not([disabled]), select:not([disabled])"

def _text_of_label(page: Page, el: Locator) -> str:
    try:
        # try associated label via id/for
        _id = el.get_attribute("id")
        if _id:
            lbl = page.locator(f'label[for="{_id}"]')
            if lbl.count():
                t = lbl.first.inner_text(timeout=500) or ""
                if t.strip():
                    return t
        # try ARIA
        aria = el.get_attribute("aria-label") or ""
        if aria.strip():
            return aria
        # try placeholder
        ph = el.get_attribute("placeholder") or ""
        if ph.strip():
            return ph
    except Exception:
        pass
    return ""

def _candidate_text(el: Locator, label_text: str) -> str:
    try:
        name = el.get_attribute("name") or ""
        _id  = el.get_attribute("id") or ""
        cls  = el.get_attribute("class") or ""
        ph   = el.get_attribute("placeholder") or ""
        aria = el.get_attribute("aria-label") or ""
        title= el.get_attribute("title") or ""
    except Exception:
        name=_id=cls=ph=aria=title=""
    blob = " ".join([label_text, name, _id, cls, ph, aria, title]).lower()
    return blob

def _score(blob: str, tokens: List[str]) -> int:
    s = 0
    for tok in tokens:
        if tok in blob:
            s += 3
        # edge cases: exact name match like name="email"
        if f'name="{tok}"' in blob:
            s += 2
    return s

def build_fill_plan(page: Page, form_index: int, user_profile: Dict) -> List[Tuple[str, str, str]]:
    """
    Returns a list of (selector, value, label_for_log)
    We scan inputs inside the form, choose the best profile field for each, and produce a sane value.
    """
    plan: List[Tuple[str, str, str]] = []
    form = page.locator("form").nth(form_index)
    inputs = form.locator(INPUT_SELECTOR)
    count = inputs.count() if inputs else 0
    if count == 0:
        return plan

    for i in range(count):
        el = inputs.nth(i)
        try:
            tag = (el.evaluate("e=>e.tagName") or "").lower()
            itype = (el.get_attribute("type") or "").lower()
        except Exception:
            tag, itype = "", ""

        label_text = _text_of_label(page, el).lower()
        blob = _candidate_text(el, label_text)

        # special cases first
        if tag == "textarea":
            val = user_profile.get("message") or user_profile.get("notes") or ""
            if val:
                plan.append((f"FORM>>{form_index}>>EL#{i}", val, "message/notes"))
            continue

        if tag == "select":
            # try to pick an option using profile value that matches text/value
            cand_key, cand_val = _best_profile_key_for(blob, user_profile)
            if cand_key and cand_val:
                plan.append((f"FORM>>{form_index}>>EL#{i}::select::{cand_key}", str(cand_val), cand_key))
            continue

        if itype in ("checkbox", "radio"):
            # only toggle checkbox for boolean-like profile fields
            if "existing customer" in blob or "existing_customer" in blob or "is_existing_customer" in blob:
                if bool(user_profile.get("is_existing_customer", False)):
                    plan.append((f"FORM>>{form_index}>>EL#{i}::check", "true", "is_existing_customer"))
            continue

        # text-like inputs
        cand_key, cand_val = _best_profile_key_for(blob, user_profile)
        if cand_key and cand_val:
            plan.append((f"FORM>>{form_index}>>EL#{i}", str(cand_val), cand_key))
            continue

        # last resort: email/name heuristic
        if itype == "email" and user_profile.get("email"):
            plan.append((f"FORM>>{form_index}>>EL#{i}", user_profile["email"], "email"))
            continue
        if "name" in blob:
            full = f"{user_profile.get('first_name','').strip()} {user_profile.get('last_name','').strip()}".strip()
            if full:
                plan.append((f"FORM>>{form_index}>>EL#{i}", full, "full_name"))
                continue

    return plan

def _best_profile_key_for(blob: str, user_profile: Dict) -> Tuple[Optional[str], Optional[str]]:
    best_key, best_val, best_score = None, None, 0
    for key, toks in PROFILE_TOKENS.items():
        if key not in user_profile:
            continue
        val = user_profile.get(key)
        if val in (None, "", False):
            continue
        sc = _score(blob, toks)
        if sc > best_score:
            best_key, best_val, best_score = key, val, sc
    return best_key, (str(best_val) if best_val is not None else None)
