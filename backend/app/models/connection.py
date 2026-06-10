"""
知识关联模型

记录两条资料之间的语义关联，由 AI 分析生成。
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MaterialConnection(Base):
    """
    资料间关联

    relation_type 类型说明：
    - prerequisite: A 是 B 的前置知识（先学 A 再学 B）
    - extends:      B 是 A 的延伸/深入
    - related:      两者内容相关
    - contradicts:  两者观点矛盾
    """
    __tablename__ = "material_connections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID 主键"
    )

    material1_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="资料 A 的 ID"
    )
    material2_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="资料 B 的 ID"
    )

    relation_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="关联类型：prerequisite / extends / related / contradicts"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="关联说明（AI 生成）"
    )
    strength: Mapped[float] = mapped_column(
        Float, default=0.5,
        comment="关联强度 0.0 ~ 1.0"
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow,
        comment="生成时间"
    )
