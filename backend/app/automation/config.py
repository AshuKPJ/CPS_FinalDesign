# backend/app/automation/config.py

import os
from pathlib import Path

def _int_env(name: str, default: int) -> int:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return int(v)
    except Exception:
        return default

ARTIFACTS_ROOT = Path("run_artifacts")
PROFILE_DIR = ARTIFACTS_ROOT / "profile"
SCREENSHOTS_DIR = ARTIFACTS_ROOT / "screenshots"

NAV_TIMEOUT_MS = _int_env("NAV_TIMEOUT_MS", 45_000)
BROWSER_NAME = os.getenv("BROWSER_NAME", "firefox").strip().lower()
