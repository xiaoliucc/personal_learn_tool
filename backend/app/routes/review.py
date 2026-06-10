"""复习路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services import review_service

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/due")
async def get_due_reviews(db: AsyncSession = Depends(get_db)):
    """获取到期的复习资料"""
    items = await review_service.get_due_reviews(db)
    # 加载资料标题
    from ..models.material import Material
    from sqlalchemy import select
    enriched = []
    for item in items:
        m = await db.get(Material, item["material_id"])
        enriched.append({**item, "material_title": m.title if m else "(已删除)"})
    return enriched


@router.get("/due/count")
async def get_due_count(db: AsyncSession = Depends(get_db)):
    """获取到期复习数量"""
    count = await review_service.get_due_count(db)
    return {"count": count}


@router.post("/add/{material_id}")
async def add_to_review(material_id: str, db: AsyncSession = Depends(get_db)):
    """将资料加入复习队列"""
    try:
        item = await review_service.add_to_review(db, material_id)
        return {"id": item.id, "material_id": item.material_id, "message": "已加入复习"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record/{review_id}")
async def record_review(
    review_id: str,
    quality: int = Query(..., ge=0, le=5),
    db: AsyncSession = Depends(get_db),
):
    """记录复习结果（quality: 0=完全忘记, 3=勉强, 5=完美）"""
    try:
        item = await review_service.record_review(db, review_id, quality)
        return {
            "id": item.id,
            "ease_factor": item.ease_factor,
            "interval": item.interval,
            "repetitions": item.repetitions,
            "next_review_at": item.next_review_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
