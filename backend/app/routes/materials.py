"""
资料 CRUD 路由

提供资料的标准增删改查接口，支持：
- 分页列表查询（可按类型和标签筛选）
- 详情查询（含关联标签）
- 创建/更新/删除
- 触发 AI 处理（后续阶段实现）
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.material import Material, Tag, MaterialTag
from ..schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    MaterialListResponse,
    TagBrief,
    SummaryBrief,
)

router = APIRouter(prefix="/api/materials", tags=["materials"])


# =============================================================================
# 辅助函数
# =============================================================================

def _material_to_response(material: Material) -> MaterialResponse:
    """将 ORM 对象转换为响应模型"""
    # 摘要
    summary = None
    if material.summary:
        summary = SummaryBrief(
            content=material.summary.content,
            key_points=material.summary.key_points,
            model_used=material.summary.model_used,
            generated_at=material.summary.generated_at,
        )

    return MaterialResponse(
        id=material.id,
        type=material.type.value,
        title=material.title,
        content=material.content,
        url=material.url,
        language=material.language,
        source=material.source,
        is_processed=material.is_processed,
        tags=[
            TagBrief(id=mt.tag.id, name=mt.tag.name, color=mt.tag.color, confidence=mt.confidence)
            for mt in material.tags
        ],
        summary=summary,
        created_at=material.created_at,
        updated_at=material.updated_at,
    )


# =============================================================================
# API 端点
# =============================================================================

@router.get("", response_model=MaterialListResponse)
async def list_materials(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    type: str | None = Query(None, description="按类型筛选"),
    tag: str | None = Query(None, description="按标签 ID 筛选"),
    search: str | None = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取资料列表，支持分页和筛选。

    - **page**: 页码（从 1 开始）
    - **page_size**: 每页数量（1-100，默认 20）
    - **type**: 按类型筛选 (note/link/snippet)
    - **tag**: 按标签 ID 筛选
    - **search**: 按标题和内容搜索关键词
    """
    # 基础查询
    query = select(Material).options(selectinload(Material.tags).selectinload(MaterialTag.tag)).options(selectinload(Material.summary))

    # 按类型筛选
    if type:
        query = query.where(Material.type == type)

    # 按标签筛选（通过中间表关联）
    if tag:
        query = query.join(Material.tags).where(MaterialTag.tag_id == tag)

    # 关键词搜索（后续阶段会用 FTS5 替换此简单 LIKE 搜索）
    if search:
        query = query.where(
            (Material.title.contains(search)) | (Material.content.contains(search))
        )

    # 按创建时间倒序排列
    query = query.order_by(Material.created_at.desc())

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页查询
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    materials = result.scalars().unique().all()

    return MaterialListResponse(
        items=[_material_to_response(m) for m in materials],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个资料详情，包含关联标签"""
    query = (
        select(Material)
        .options(selectinload(Material.tags).selectinload(MaterialTag.tag)).options(selectinload(Material.summary))
        .where(Material.id == material_id)
    )
    result = await db.execute(query)
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    return _material_to_response(material)


@router.post("", response_model=MaterialResponse, status_code=201)
async def create_material(
    body: MaterialCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新资料"""
    material = Material(
        type=body.type,
        title=body.title,
        content=body.content,
        url=body.url,
        language=body.language,
        source=body.source,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)

    # 重新查询以加载关联关系
    return await _get_material_with_tags(material.id, db)


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: str,
    body: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新资料（只更新传入的字段）"""
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    # 只更新传入的非空字段
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)

    await db.commit()
    await db.refresh(material)
    return await _get_material_with_tags(material_id, db)


@router.delete("/{material_id}", status_code=204)
async def delete_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除资料（关联的 MaterialTag 由 cascade 自动删除）"""
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    await db.delete(material)
    await db.commit()


# =============================================================================
# 内部辅助
# =============================================================================

async def _get_material_with_tags(material_id: str, db: AsyncSession) -> MaterialResponse:
    """查询资料并转换为响应模型"""
    query = (
        select(Material)
        .options(selectinload(Material.tags).selectinload(MaterialTag.tag)).options(selectinload(Material.summary))
        .where(Material.id == material_id)
    )
    result = await db.execute(query)
    material = result.scalar_one()
    return _material_to_response(material)
