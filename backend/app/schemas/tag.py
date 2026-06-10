"""
标签相关的 Pydantic Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """创建标签时的请求体"""
    name: str = Field(..., min_length=1, max_length=100, description="标签名称")
    color: str = Field(default="#6366f1", pattern="^#[0-9a-fA-F]{6}$", description="标签颜色")
    parent_id: Optional[str] = Field(None, description="父标签 ID（可选）")
    description: Optional[str] = Field(None, max_length=500, description="标签描述")


class TagUpdate(BaseModel):
    """更新标签时的请求体"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="标签名称")
    color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$", description="标签颜色")
    parent_id: Optional[str] = Field(None, description="父标签 ID")
    description: Optional[str] = Field(None, max_length=500, description="标签描述")


class TagResponse(BaseModel):
    """返回标签详情时的响应体"""
    id: str
    name: str
    color: str
    parent_id: Optional[str] = None
    description: Optional[str] = None
    children: list["TagResponse"] = []  # 子标签列表

    model_config = {"from_attributes": True}
