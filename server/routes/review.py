"""待确认队列:中低置信度的归类停在这里,等用户批准/改派/拒绝。"""
import json

from fastapi import APIRouter, HTTPException

from .. import db
from ..models import ReviewAction, TopicDecision

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("")
def list_pending():
    items = db.list_captures(status="awaiting_review", limit=100)
    for cap in items:
        cap["suggestion"] = json.loads(cap["suggestion"]) if cap["suggestion"] else None
        if cap["suggestion"] and cap["suggestion"].get("topic_id"):
            topic = db.get_topic(cap["suggestion"]["topic_id"])
            cap["suggestion"]["topic_title"] = topic["title"] if topic else None
    return items


@router.post("/{capture_id}")
async def decide(capture_id: str, action: ReviewAction):
    cap = db.get_capture(capture_id)
    if not cap:
        raise HTTPException(404, "capture 不存在")
    if cap["status"] != "awaiting_review":
        raise HTTPException(400, f"状态 {cap['status']} 不在待确认队列")

    decision = TopicDecision.model_validate_json(cap["suggestion"])

    if action.action == "reject":
        db.update_capture(capture_id, status="rejected")
        db.log(capture_id, "review", "ok", "用户拒绝归档")
        return {"ok": True, "status": "rejected"}

    if action.action == "reassign":
        if action.topic_id:
            if not db.get_topic(action.topic_id):
                raise HTTPException(404, "改派的目标主题不存在")
            decision.action = "existing"
            decision.topic_id = action.topic_id
        elif action.new_topic_title:
            decision.action = "new"
            decision.new_topic_title = action.new_topic_title
        else:
            raise HTTPException(400, "reassign 需要 topic_id 或 new_topic_title")
        db.log(capture_id, "review", "ok", f"用户改派: {action.model_dump_json()}")
    else:
        db.log(capture_id, "review", "ok", "用户批准 AI 建议")

    from ..pipeline.worker import run_merge
    await run_merge(capture_id, decision)
    return db.get_capture(capture_id)
