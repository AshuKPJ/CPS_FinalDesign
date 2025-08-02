# backend/app/automation/captcha_solver.py

import requests

async def solve_captcha(image_bytes, username, password):
    # DeathByCaptcha API integration
    response = requests.post(
        "http://api.dbcapi.me/api/captcha",
        auth=(username, password),
        files={"captchafile": ("captcha.jpg", image_bytes)},
    )
    if response.status_code == 200:
        return response.json().get("text", "")
    return None
