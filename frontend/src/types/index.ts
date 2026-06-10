// =============================================================================
// 前端类型定义 — 与后端 Pydantic Schemas 对应
// =============================================================================

/** 资料类型 */
export type MaterialType = 'note' | 'link' | 'snippet'

/** AI 摘要 */
export interface Summary {
  content: string
  key_points: string[] | null
  model_used: string | null
  generated_at: string | null
}

/** 资料列表项 */
export interface Material {
  id: string
  type: MaterialType
  title: string
  content: string | null
  url: string | null
  language: string | null
  source: string | null
  is_processed: boolean
  tags: TagBrief[]
  summary: Summary | null
  created_at: string
  updated_at: string
}

/** 标签简要信息（内嵌在 Material 中） */
export interface TagBrief {
  id: string
  name: string
  color: string
  confidence: number | null
}

/** 标签（含层级） */
export interface Tag {
  id: string
  name: string
  color: string
  parent_id: string | null
  description: string | null
  children: Tag[]
}

/** 分页列表响应 */
export interface MaterialListResponse {
  items: Material[]
  total: number
  page: number
  page_size: number
}

/** 创建资料请求 */
export interface MaterialCreate {
  type: MaterialType
  title: string
  content?: string
  url?: string
  language?: string
  source?: string
}

/** 更新资料请求（所有字段可选） */
export interface MaterialUpdate {
  type?: MaterialType
  title?: string
  content?: string
  url?: string
  language?: string
  source?: string
}

/** 创建标签请求 */
export interface TagCreate {
  name: string
  color?: string
  parent_id?: string
  description?: string
}

/** 更新标签请求 */
export interface TagUpdate {
  name?: string
  color?: string
  parent_id?: string
  description?: string
}

// =============================================================================
// 知识图谱
// =============================================================================

/** 图谱节点 */
export interface GraphNode {
  id: string
  title: string
  type: MaterialType
  tags: TagBrief[]
  is_processed: boolean
}

/** 图谱边 */
export interface GraphEdge {
  id: string
  source: string
  target: string
  relation_type: string
  description: string | null
  strength: number
}

/** 图谱数据 */
export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}
