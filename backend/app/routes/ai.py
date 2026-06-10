"""
AI 操作路由

提供 AI 驱动的资料处理接口：
- classify: 自动打标签
- summarize: 生成摘要
- process: 编排接口（分类 + 摘要）
- WebSocket: 实时进度推送
"""

import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.material import Material, Tag, MaterialTag
from ..models.summary import Summary
from ..models.connection import MaterialConnection
from ..services import ai_service
from ..ws_manager import ws_manager

router = APIRouter(prefix="/api/ai", tags=["ai"])


# =============================================================================
# WebSocket — AI 处理进度
# =============================================================================

@router.websocket("/ws/processing")
async def websocket_processing(websocket: WebSocket):
    """AI 处理进度推送。消息格式：{task_id, status, progress, message}"""
    await ws_manager.connect(websocket)
    try:
        # 保持连接，等待客户端关闭
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# =============================================================================
# REST API
# =============================================================================

@router.post("/classify/{material_id}")
async def classify_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    对指定资料进行 AI 自动分类/标签推荐。

    返回 AI 建议的标签列表（不会自动保存，由用户确认后保存）。
    """
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    try:
        result = await ai_service.classify_material(material.title, material.content)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 分类失败：{e}")


@router.post("/summarize/{material_id}")
async def summarize_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    对指定资料生成 AI 摘要和关键要点。

    自动保存摘要到数据库（覆盖已有摘要）。
    """
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    try:
        result = await ai_service.summarize_material(material.title, material.content)

        # 保存或更新摘要
        existing = (
            await db.execute(select(Summary).where(Summary.material_id == material_id))
        ).scalar_one_or_none()

        if existing:
            existing.content = result["summary"]
            existing.key_points = result.get("key_points", [])
            existing.model_used = ai_service.DEFAULT_MODEL
        else:
            summary = Summary(
                material_id=material_id,
                content=result["summary"],
                key_points=result.get("key_points", []),
                model_used=ai_service.DEFAULT_MODEL,
            )
            db.add(summary)

        await db.commit()
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 摘要失败：{e}")


@router.post("/connect/{material_id}")
async def connect_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    发现资料与已有资料之间的关联，自动保存到数据库。
    """
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    try:
        # 获取已有资料列表（排除自身）
        from sqlalchemy.orm import selectinload
        existing_result = await db.execute(
            select(Material)
            .options(selectinload(Material.summary))
            .where(Material.id != material_id)
        )
        existing = existing_result.scalars().all()

        existing_list = [
            {
                "id": m.id,
                "title": m.title,
                "summary": m.summary.content if m.summary else None,
            }
            for m in existing
        ]

        connections = await ai_service.find_connections(
            material.title,
            material.content,
            existing_list,
        )

        # 保存关联
        saved = 0
        for conn in connections:
            target_id = conn.get("material_id", "")
            if not target_id:
                continue
            # 检查是否已存在相同关联
            from sqlalchemy import and_, or_
            dup_query = select(MaterialConnection).where(
                or_(
                    and_(MaterialConnection.material1_id == material_id,
                         MaterialConnection.material2_id == target_id),
                    and_(MaterialConnection.material1_id == target_id,
                         MaterialConnection.material2_id == material_id),
                )
            )
            dup_result = await db.execute(dup_query)
            if dup_result.scalar_one_or_none():
                continue

            db.add(MaterialConnection(
                material1_id=material_id,
                material2_id=target_id,
                relation_type=conn.get("relation_type", "related"),
                description=conn.get("description", ""),
                strength=conn.get("strength", 0.5),
            ))
            saved += 1

        await db.commit()
        return {"connections_found": len(connections), "connections_saved": saved}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"关联发现失败：{e}")


@router.post("/process/{material_id}")
async def process_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    对资料执行完整的 AI 处理（分类 + 摘要 + 关联）。

    通过 WebSocket 推送实时进度。
    返回 task_id，前端通过 WebSocket 监听进度。
    """
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    task_id = str(uuid.uuid4())[:8]

    # 定义进度回调
    async def progress(progress: float, message: str):
        await ws_manager.broadcast({
            "task_id": task_id,
            "status": "completed" if progress >= 1.0 else "running",
            "progress": progress,
            "message": message,
            "material_id": material_id,
        })

    # 后台执行 AI 处理
    asyncio.create_task(_do_process(material, task_id, progress, db))

    return {"task_id": task_id, "message": "AI 处理已开始，请通过 WebSocket 监听进度"}


# =============================================================================
# 内部
# =============================================================================

async def _do_process(
    material: Material,
    task_id: str,
    progress_callback,
    db: AsyncSession,
):
    """后台执行完整的 AI 处理流程，并将结果写入数据库。"""
    try:
        result = await ai_service.process_material(
            title=material.title,
            content=material.content,
            progress_callback=progress_callback,
        )

        # 保存摘要
        if result.get("summary"):
            existing = (
                await db.execute(select(Summary).where(Summary.material_id == material.id))
            ).scalar_one_or_none()
            if existing:
                existing.content = result["summary"]
                existing.key_points = result.get("key_points", [])
                existing.model_used = ai_service.DEFAULT_MODEL
            else:
                db.add(Summary(
                    material_id=material.id,
                    content=result["summary"],
                    key_points=result.get("key_points", []),
                    model_used=ai_service.DEFAULT_MODEL,
                ))

        # 保存 AI 建议的标签（低置信度的待确认标签）
        for tag_data in result.get("tags", []):
            # 查找或创建标签
            tag_query = select(Tag).where(Tag.name == tag_data["name"])
            tag_result = await db.execute(tag_query)
            tag = tag_result.scalar_one_or_none()

            if not tag:
                tag = Tag(
                    name=tag_data["name"],
                    color=tag_data.get("color", "#6366f1"),
                )
                db.add(tag)
                await db.flush()  # 获取 tag.id

            # 检查关联是否已存在
            from sqlalchemy import and_
            mt_query = select(MaterialTag).where(
                and_(
                    MaterialTag.material_id == material.id,
                    MaterialTag.tag_id == tag.id,
                )
            )
            mt_result = await db.execute(mt_query)
            if not mt_result.scalar_one_or_none():
                db.add(MaterialTag(
                    material_id=material.id,
                    tag_id=tag.id,
                    confidence=tag_data.get("confidence", 0.8),
                ))

        # 标记处理完成
        material.is_processed = True
        await db.commit()

    except Exception as e:
        await progress_callback(0.0, f"处理失败：{e}")
