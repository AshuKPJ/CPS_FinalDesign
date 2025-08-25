from __future__ import annotations
from typing import Optional, Tuple, Dict, Any
import json
import time

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None
import requests

DBC_BASE = "http://api.dbcapi.me"

def _post_sync(path: str, auth: Tuple[str, str], data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    url = f"{DBC_BASE}{path}"
    try:
        if httpx:
            r = httpx.post(url, auth=auth, data=data, timeout=30)
            if r.status_code == 200:
                return r.json()
            return None
        r = requests.post(url, auth=auth, data=data, timeout=30)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def _get_sync(path: str, auth: Tuple[str, str]) -> Optional[Dict[str, Any]]:
    url = f"{DBC_BASE}{path}"
    try:
        if httpx:
            r = httpx.get(url, auth=auth, timeout=30)
            if r.status_code == 200:
                return r.json()
            return None
        r = requests.get(url, auth=auth, timeout=30)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def solve_recaptcha_v2_token_sync(
    site_key: str,
    page_url: str,
    username: str,
    password: str,
    timeout_sec: int = 120,
    poll_interval_sec: float = 4.0,
) -> Optional[str]:
    """
    Use DeathByCaptcha TOKEN method to solve reCAPTCHA v2/v2-invisible.
    Returns the response token (string) or None on failure.

    API summary (DBC):
      POST /api/captcha with form { type: 4, token_params: '{"googlekey":"<key>","pageurl":"<url>"}' }
      → { "captcha": <id>, ... }          # id name may vary, handle "captcha"/"captcha_id"/"id"
      Then poll: GET /api/captcha/<id> → { "text": "<token>", "status": "solved"|... }
    """
    auth = (username, password)
    payload = {
        "type": 4,  # token task
        "token_params": json.dumps({"googlekey": site_key, "pageurl": page_url}),
    }

    first = _post_sync("/api/captcha", auth, payload)
    if not first:
        return None

    cap_id = first.get("captcha") or first.get("captcha_id") or first.get("id")
    if not cap_id:
        return None

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        res = _get_sync(f"/api/captcha/{cap_id}", auth)
        if res and (token := res.get("text")):
            return token
        time.sleep(poll_interval_sec)

    return None

# (Optional) generic image solver (kept for completeness / compatibility)
def solve_captcha_sync(image_bytes: bytes, username: str, password: str) -> Optional[str]:
    try:
        files = {"captchafile": ("captcha.jpg", image_bytes)}
        url = f"{DBC_BASE}/api/captcha"
        if httpx:
            r = httpx.post(url, auth=(username, password), files=files, timeout=30)
            if r.status_code == 200:
                j = r.json()
                return j.get("text")
            return None
        r = requests.post(url, auth=(username, password), files=files, timeout=30)
        if r.status_code == 200:
            return (r.json() or {}).get("text")
    except Exception:
        return None
    return None
