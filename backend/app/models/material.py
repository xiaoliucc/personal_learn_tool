"""
学习资料核心模型

定义了 Material（资料）、Tag（标签）、MaterialTag（资料-标签关联）三个模型。
- Material 支持三种类型：note（笔记）、link（链接）、snippet（代码片段）
- Tag 支持两级层级结构（parent_id 自引用）
- MaterialTag 记录 AI 建议标签的置信度
"""

import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, Enum as SAEnum, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base


# 辅助函数：返回当前 UTC 时间
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# =============================================================================
# 枚举类型
# =============================================================================

class MaterialType(str, enum.Enum):
    """资料类型枚举"""
    note = "note"        # 文本笔记/摘录
    link = "link"        # 网页链接
    snippet = "snippet"  # 代码片段


# =============================================================================
# Material — 学习资料
# =============================================================================

class Material(Base):
    """
    学习资料主表

    存储用户收集的所有学习资料。不同类型通过 type 字段区分：
    - note: 文本笔记，content 为主要内容
    - link: 网页链接，url 为链接地址，content 可为网页抓取内容
    - snippet: 代码片段，language 标记编程语言
    """
    __tablename__ = "materials"

    # ---- 主键 ----
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID 主键"
    )

    # ---- 基本字段 ----
    type: Mapped[MaterialType] = mapped_column(
        SAEnum(MaterialType), nullable=False,
        comment="资料类型：note / link / snippet"
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False,
        comment="资料标题"
    )
    content: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="正文内容（Markdown 格式，link 类型可为空）"
    )
    url: Mapped[str | None] = mapped_column(
        String(2000), nullable=True,
        comment="原始链接（link 类型使用）"
    )
    language: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="编程语言（snippet 类型使用，如 python、typescript）"
    )
    source: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="资料来源（如书名、课程名、作者）"
    )
    is_processed: Mapped[bool] = mapped_column(
        Boolean, default=False,
        comment="是否已被 AI 处理（分类+摘要+关联）"
    )

    # ---- 时间戳 ----
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow,
        comment="最后更新时间"
    )

    # ---- 关联关系 ----
    # 与 Tag 的多对多关系（通过 MaterialTag 中间表）
    # lazy="selectin" 查询时自动联表，避免 N+1 查询问题
    tags: Mapped[list["MaterialTag"]] = relationship(
        back_populates="material",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # 与 Summary 的一对一关系
    summary: Mapped["Summary | None"] = relationship(
        back_populates="material",
        uselist=False,          # 一对一（非列表）
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Material(id={self.id}, type={self.type.value}, title={self.title!r})>"


# =============================================================================
# Tag — 标签
# =============================================================================

class Tag(Base):
    """
    标签表

    支持两级层级结构：parent_id 指向父标签，形成树形关系。
    例如：Python（父标签）→ asyncio（子标签）
    前端筛选时，选择父标签自动包含其所有子标签的资料。
    """
    __tablename__ = "tags"

    # ---- 主键 ----
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID 主键"
    )

    # ---- 基本字段 ----
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False,
        comment="标签名称（全局唯一）"
    )
    color: Mapped[str] = mapped_column(
        String(7), default="#6366f1",
        comment="标签颜色（十六进制格式，如 #6366f1）"
    )
    parent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tags.id"), nullable=True,
        comment="父标签 ID，NULL 表示顶级标签"
    )
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="标签描述（可选）"
    )

    # ---- 关联关系 ----
    # 与 Material 的多对多关系（通过 MaterialTag 中间表）
    materials: Mapped[list["MaterialTag"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan"
    )

    # 自引用：父子标签层级关系
    # parent: 多对一（子→父），remote_side 指向"一"侧的主键 Tag.id
    parent: Mapped["Tag | None"] = relationship(
        "Tag", back_populates="children",
        remote_side="Tag.id"    # Tag.id 是"远程"侧（被外键指向的列）
    )
    # children: 一对多（父→子），自动获取 parent_id 指向当前标签的所有子标签
    children: Mapped[list["Tag"]] = relationship(
        "Tag", back_populates="parent",
        lazy="selectin",
        order_by="Tag.name"     # 子标签按名称排序
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name!r})>"


# =============================================================================
# MaterialTag — 资料-标签关联（多对多中间表）
# =============================================================================

class MaterialTag(Base):
    """
    资料与标签的多对多关联表

    除了基本的外键关联外，额外存储 confidence 字段，
    用于标记 AI 建议标签的置信度（0.0 ~ 1.0）。
    手动添加的标签 confidence 为 1.0。
    """
    __tablename__ = "material_tags"

    # ---- 联合主键（material_id + tag_id） ----
    material_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("materials.id", ondelete="CASCADE"),
        primary_key=True,
        comment="资料 ID"
    )
    tag_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        comment="标签 ID"
    )

    # ---- 额外字段 ----
    confidence: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="AI 建议标签的置信度（0.0~1.0），手动标签为 None"
    )

    # ---- 关联关系 ----
    material: Mapped["Material"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(back_populates="materials")

    def __repr__(self) -> str:
        return f"<MaterialTag(material={self.material_id}, tag={self.tag_id})>"
