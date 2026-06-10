"""
知识图谱路由

返回前端可视化需要的节点和边数据。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.material import Material, MaterialTag
from ..models.connection import MaterialConnection

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/graph")
async def get_graph(db: AsyncSession = Depends(get_db)):
    """
    返回知识图谱数据：
    - nodes: 所有资料节点（id, title, type, tags）
    - edges: 所有关联边（source, target, relation_type, description）
    """
    # 查询所有资料
    materials_result = await db.execute(
        select(Material).options(selectinload(Material.tags).selectinload(MaterialTag.tag))
    )
    materials = materials_result.scalars().unique().all()

    # 查询所有关联
    connections_result = await db.execute(select(MaterialConnection))
    connections = connections_result.scalars().all()

    # 构建节点
    nodes = []
    for m in materials:
        nodes.append({
            "id": m.id,
            "title": m.title,
            "type": m.type.value if hasattr(m.type, 'value') else m.type,
            "tags": [{"id": mt.tag.id, "name": mt.tag.name, "color": mt.tag.color}
                     for mt in m.tags],
            "is_processed": m.is_processed,
        })

    # 构建边
    edges = []
    for c in connections:
        edges.append({
            "id": c.id,
            "source": c.material1_id,
            "target": c.material2_id,
            "relation_type": c.relation_type,
            "description": c.description,
            "strength": c.strength,
        })

    return {"nodes": nodes, "edges": edges}
