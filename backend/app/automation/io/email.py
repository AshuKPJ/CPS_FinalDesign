# backend/app/automation/email_utils.py

import re
from typing import List, Set

EMAIL_RE = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE
)

def extract_emails_from_text(text: str) -> List[str]:
    if not text:
        return []
    found: Set[str] = set(m.group(0) for m in EMAIL_RE.finditer(text))
    # simple de-dup + normalize
    return sorted({e.strip().lower() for e in found})
