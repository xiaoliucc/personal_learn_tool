"""数据导出路由 — JSON 备份 + Markdown 文件"""

import json
import zipfile
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.material import Material, Tag, MaterialTag
from ..models.summary import Summary
from ..models.connection import MaterialConnection

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/json")
async def export_json(db: AsyncSession = Depends(get_db)):
    """导出所有资料为 JSON 备份文件"""
    materials_result = await db.execute(
        select(Material)
        .options(selectinload(Material.tags).selectinload(MaterialTag.tag))
        .options(selectinload(Material.summary))
    )
    materials = materials_result.scalars().unique().all()

    # 标签
    tags_result = await db.execute(select(Tag))
    tags = tags_result.scalars().all()

    # 关联
    conns_result = await db.execute(select(MaterialConnection))
    connections = conns_result.scalars().all()

    data = {
        "exported_at": __import__("datetime").datetime.now().isoformat(),
        "materials": [
            {
                "id": m.id,
                "type": m.type.value if hasattr(m.type, "value") else m.type,
                "title": m.title,
                "content": m.content,
                "url": m.url,
                "language": m.language,
                "source": m.source,
                "tags": [
                    {"name": mt.tag.name, "confidence": mt.confidence}
                    for mt in m.tags
                ],
                "summary": m.summary.content if m.summary else None,
                "key_points": m.summary.key_points if m.summary else None,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            }
            for m in materials
        ],
        "tags": [{"id": t.id, "name": t.name, "color": t.color, "parent_id": t.parent_id} for t in tags],
        "connections": [
            {
                "material1_id": c.material1_id,
                "material2_id": c.material2_id,
                "relation_type": c.relation_type,
                "description": c.description,
                "strength": c.strength,
            }
            for c in connections
        ],
    }

    return data


@router.get("/markdown")
async def export_markdown(db: AsyncSession = Depends(get_db)):
    """导出所有资料为 Markdown .zip 文件（每篇一个 .md，含 frontmatter）"""
    materials_result = await db.execute(
        select(Material)
        .options(selectinload(Material.tags).selectinload(MaterialTag.tag))
        .options(selectinload(Material.summary))
    )
    materials = materials_result.scalars().unique().all()

    # 在内存中创建 zip
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for m in materials:
            # 构建 frontmatter
            fm = "---\n"
            fm += f"title: \"{m.title}\"\n"
            fm += f"type: {m.type.value if hasattr(m.type, 'value') else m.type}\n"
            if m.source:
                fm += f"source: \"{m.source}\"\n"
            if m.url:
                fm += f"url: \"{m.url}\"\n"
            if m.language:
                fm += f"language: {m.language}\n"
            tags = [mt.tag.name for mt in m.tags]
            if tags:
                fm += f"tags: [{', '.join(tags)}]\n"
            fm += f"created: {m.created_at.isoformat() if m.created_at else ''}\n"
            fm += "---\n\n"
            fm += f"# {m.title}\n\n"
            if m.summary:
                fm += f"> **AI 摘要**：{m.summary.content}\n\n"
                if m.summary.key_points:
                    for pt in m.summary.key_points:
                        fm += f"- {pt}\n"
                    fm += "\n"
            if m.content:
                fm += m.content
            else:
                fm += "（无正文内容）"

            # 文件名：去除非法字符
            safe_name = "".join(c for c in m.title if c.isalnum() or c in " _-（）()")[:50]
            zf.writestr(f"{safe_name}.md", fm)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=learning-collector-export.zip"},
    )
