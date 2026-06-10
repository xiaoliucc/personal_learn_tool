"""
资料相关的 Pydantic Schemas

定义了资料的请求验证和响应序列化模型。
- MaterialCreate: 创建资料时的请求体
- MaterialUpdate: 更新资料时的请求体（所有字段可选）
- MaterialResponse: 返回资料详情时的响应体
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# =============================================================================
# Material Schemas
# =============================================================================

class MaterialCreate(BaseModel):
    """创建材料时的请求体"""
    type: str = Field(..., pattern="^(note|link|snippet)$", description="资料类型")
    title: str = Field(..., min_length=1, max_length=500, description="标题")
    content: Optional[str] = Field(None, description="正文内容")
    url: Optional[str] = Field(None, max_length=2000, description="原始链接")
    language: Optional[str] = Field(None, max_length=50, description="编程语言")
    source: Optional[str] = Field(None, max_length=500, description="来源")


class MaterialUpdate(BaseModel):
    """更新资料时的请求体（所有字段可选，只传要更新的字段）"""
    type: Optional[str] = Field(None, pattern="^(note|link|snippet)$", description="资料类型")
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="标题")
    content: Optional[str] = Field(None, description="正文内容")
    url: Optional[str] = Field(None, max_length=2000, description="原始链接")
    language: Optional[str] = Field(None, max_length=50, description="编程语言")
    source: Optional[str] = Field(None, max_length=500, description="来源")


class TagBrief(BaseModel):
    """标签简要信息（嵌入 MaterialResponse 中）"""
    id: str
    name: str
    color: str
    confidence: Optional[float] = None  # AI 建议标签的置信度

    model_config = {"from_attributes": True}


class SummaryBrief(BaseModel):
    """摘要简要信息"""
    content: str
    key_points: Optional[list[str]] = None
    model_used: Optional[str] = None
    generated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MaterialResponse(BaseModel):
    """返回资料详情时的响应体"""
    id: str
    type: str
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    language: Optional[str] = None
    source: Optional[str] = None
    is_processed: bool
    tags: list[TagBrief] = []
    summary: Optional[SummaryBrief] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MaterialListResponse(BaseModel):
    """资料列表响应（含分页信息）"""
    items: list[MaterialResponse]
    total: int
    page: int
    page_size: int

    model_config = {"from_attributes": True}
