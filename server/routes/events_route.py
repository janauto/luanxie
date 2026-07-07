"""SSE:向前端推送 capture/topic 状态变化。"""
import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .. import events

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("")
async def stream():
    async def gen():
        q = events.subscribe()
        try:
            yield "retry: 3000\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=25)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            events.unsubscribe(q)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})
