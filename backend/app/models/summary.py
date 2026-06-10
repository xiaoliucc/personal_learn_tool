"""
AI 摘要模型

每个 Material 最多有一个 Summary，由 AI 生成后存储于此。
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import JSON
from . import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Summary(Base):
    """
    AI 生成的资料摘要

    与 Material 一对一关系，包含：
    - content: 摘要正文
    - key_points: 关键要点列表（JSON 数组）
    """
    __tablename__ = "summaries"

    # ---- 主键 ----
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID 主键"
    )

    # ---- 外键（一对一） ----
    material_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("materials.id", ondelete="CASCADE"),
        unique=True, nullable=False,  # unique 保证一对一
        comment="关联的资料 ID"
    )

    # ---- 摘要内容 ----
    content: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="AI 生成的摘要正文"
    )
    key_points: Mapped[list | None] = mapped_column(
        JSON, nullable=True,
        comment="关键要点列表（JSON 数组）"
    )

    # ---- 元数据 ----
    model_used: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="生成摘要使用的模型（如 claude-sonnet-4-6）"
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow,
        comment="生成时间"
    )

    # ---- 关联关系 ----
    material: Mapped["Material"] = relationship(back_populates="summary")

    def __repr__(self) -> str:
        return f"<Summary(id={self.id}, material_id={self.material_id})>"
