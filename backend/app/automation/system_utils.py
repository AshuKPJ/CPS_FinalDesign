# backend/app/automation/system_utils.py

import sys
import asyncio
from app.log_stream import log

def ensure_windows_proactor_policy():
    if sys.platform.startswith("win"):
        try:
            current = asyncio.get_event_loop_policy().__class__.__name__
            if current != "WindowsProactorEventLoopPolicy":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                log("Event loop policy set to WindowsProactorEventLoopPolicy")
            else:
                log("Event loop policy already WindowsProactorEventLoopPolicy")
        except Exception as e:
            log(f"Could not set WindowsProactorEventLoopPolicy: {e}")
