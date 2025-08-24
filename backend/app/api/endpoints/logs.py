# backend/app/api/endpoints/logs.py
from fastapi import APIRouter, Request
from app.log_stream import event_generator

router = APIRouter(tags=["logs"])

@router.get("/stream")
async def stream_logs(request: Request):
    # event_generator returns a StreamingResponse; return it directly
    resp = event_generator(request)
    if hasattr(resp, "__await__"):
        return await resp
    return resp
