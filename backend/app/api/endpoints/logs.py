# backend/app/api/endpoints/logs.py

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.log_stream import event_generator

router = APIRouter()

@router.get("/logs/stream")
async def stream_logs(request: Request):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")
