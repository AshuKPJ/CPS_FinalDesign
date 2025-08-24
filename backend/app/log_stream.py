# backend/app/log_stream.py
from fastapi import Request
from fastapi.responses import StreamingResponse
from typing import List, Dict
import asyncio, time, threading, uuid
from collections import deque

class LogStream:
    def __init__(self, maxlen: int = 2000):
        self.q = deque(maxlen=maxlen)
        self.lock = threading.Lock()

    def log(self, msg: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg.strip()}"
        print(line)
        with self.lock:
            self.q.append(line)

    def snapshot(self, start: int = 0):
        with self.lock:
            arr = list(self.q)
        n = len(arr)
        if start >= n:
            return [], n
        return arr[start:], n

stream = LogStream()

def log(msg: str): stream.log(msg)

def _sse(line: str) -> str:
    return "data: " + line.replace("\n","\\n") + "\n\n"

async def event_generator(request: Request) -> StreamingResponse:
    async def gen():
        idx = 0
        yield _sse("🔗 Connected to CPS log stream.")
        while True:
            if await request.is_disconnected(): break
            lines, idx = stream.snapshot(idx)
            for ln in lines: yield _sse(ln)
            await asyncio.sleep(0.5)
    return StreamingResponse(gen(), media_type="text/event-stream")
