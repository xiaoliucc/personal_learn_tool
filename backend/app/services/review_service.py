"""
复习服务 — SM-2 间隔重复算法

SM-2 算法根据用户对复习卡片的评分（0-5），调整：
- ease_factor: 难度系数（越低越难）
- interval: 下次复习间隔天数
- repetitions: 连续正确次数
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.review import ReviewItem


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def sm2(
    quality: int,
    ease_factor: float,
    interval: int,
    repetitions: int,
) -> tuple[float, int, int]:
    """
    SM-2 算法核心。

    参数:
        quality: 用户评分 0-5（0=完全忘记, 3=勉强记得, 5=完美）

    返回: (new_ease_factor, new_interval, new_repetitions)
    """
    if quality >= 3:
        # 正确：更新间隔
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)

        new_repetitions = repetitions + 1
    else:
        # 忘记：重置
        new_interval = 1
        new_repetitions = 0

    # 更新难度系数
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3

    return new_ef, new_interval, new_repetitions


async def get_due_reviews(db: AsyncSession, limit: int = 20) -> list[dict]:
    """获取当前到期的复习资料（next_review_at <= now）"""
    result = await db.execute(
        select(ReviewItem)
        .where(ReviewItem.next_review_at <= utcnow())
        .order_by(ReviewItem.next_review_at)
        .limit(limit)
    )
    items = result.scalars().all()
    return [
        {
            "id": r.id,
            "material_id": r.material_id,
            "ease_factor": r.ease_factor,
            "interval": r.interval,
            "repetitions": r.repetitions,
            "next_review_at": r.next_review_at.isoformat() if r.next_review_at else None,
        }
        for r in items
    ]


async def get_due_count(db: AsyncSession) -> int:
    """获取到期复习数量"""
    result = await db.execute(
        select(ReviewItem).where(ReviewItem.next_review_at <= utcnow())
    )
    return len(result.scalars().all())


async def add_to_review(db: AsyncSession, material_id: str) -> ReviewItem:
    """将资料加入复习队列（首次）"""
    # 检查是否已存在
    existing = await db.execute(
        select(ReviewItem).where(ReviewItem.material_id == material_id)
    )
    if existing.scalar_one_or_none():
        return existing.scalar_one()

    item = ReviewItem(material_id=material_id, next_review_at=utcnow())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def record_review(
    db: AsyncSession,
    review_id: str,
    quality: int,
) -> ReviewItem:
    """记录复习结果，更新 SM-2 参数"""
    result = await db.execute(select(ReviewItem).where(ReviewItem.id == review_id))
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("复习记录不存在")

    ef, interval, reps = sm2(
        quality=quality,
        ease_factor=item.ease_factor,
        interval=item.interval,
        repetitions=item.repetitions,
    )

    item.ease_factor = ef
    item.interval = interval
    item.repetitions = reps
    item.last_reviewed_at = utcnow()
    item.next_review_at = utcnow() + timedelta(days=interval)

    await db.commit()
    await db.refresh(item)
    return item
