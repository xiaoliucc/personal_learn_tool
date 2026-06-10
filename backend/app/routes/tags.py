"""
标签 CRUD 路由

提供标签的标准增删改查接口，支持：
- 获取全部标签（含层级结构）
- 创建/更新/删除
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.material import Tag
from ..schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter(prefix="/api/tags", tags=["tags"])


# =============================================================================
# 辅助函数
# =============================================================================

def _build_tag_tree(all_tags: list[Tag]) -> list[TagResponse]:
    """
    将扁平的标签列表转换为树形结构。
    先找出顶级标签（parent_id 为 None），再递归挂载子标签。
    """
    # 先建立 id -> TagResponse 的映射
    id_map: dict[str, TagResponse] = {}
    for tag in all_tags:
        id_map[tag.id] = TagResponse(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            parent_id=tag.parent_id,
            description=tag.description,
            children=[],
        )

    # 组织树形结构：子标签挂到父标签下
    roots: list[TagResponse] = []
    for tag in all_tags:
        node = id_map[tag.id]
        if tag.parent_id and tag.parent_id in id_map:
            id_map[tag.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


# =============================================================================
# API 端点
# =============================================================================

@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    """
    获取所有标签（返回树形结构）。
    顶级标签包含其 children（子标签），子标签不再嵌套。
    """
    # 使用 selectinload 预加载子标签，避免 N+1 查询
    query = select(Tag).options(selectinload(Tag.children))
    result = await db.execute(query)
    tags = result.scalars().unique().all()

    return _build_tag_tree(list(tags))


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    body: TagCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新标签"""
    # 如果指定了 parent_id，验证父标签存在
    if body.parent_id:
        parent = await db.get(Tag, body.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="父标签不存在")

    tag = Tag(
        name=body.name,
        color=body.color,
        parent_id=body.parent_id,
        description=body.description,
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        parent_id=tag.parent_id,
        description=tag.description,
        children=[],
    )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    body: TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新标签"""
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    await db.commit()
    await db.refresh(tag)

    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        parent_id=tag.parent_id,
        description=tag.description,
        children=[],
    )


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除标签（关联的 MaterialTag 由 cascade 自动删除）"""
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    await db.delete(tag)
    await db.commit()
