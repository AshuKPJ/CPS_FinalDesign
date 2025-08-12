# backend/app/log_stream.py
from fastapi import Request
from typing import List
import asyncio

log_queue: List[str] = []

def log(message: str):
    # trim and ignore empty/whitespace-only messages
    msg = (message or "").strip()
    if not msg:
        return
    print(msg)
    log_queue.append(msg)

async def event_generator(request: Request):
    last_index = 0
    while True:
        if await request.is_disconnected():
            break
        await asyncio.sleep(0.5)
        if last_index < len(log_queue):
            new_logs = log_queue[last_index:]
            last_index = len(log_queue)
            for line in new_logs:
                yield f"data: {line}\n\n"
