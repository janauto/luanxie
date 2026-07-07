"""手动触发导出到 Obsidian。"""
from fastapi import APIRouter

from .. import exporter

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("")
def export_now():
    exported = exporter.export_all()
    return {"exported": exported, "count": len(exported)}
