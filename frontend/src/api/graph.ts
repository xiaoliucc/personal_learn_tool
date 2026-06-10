/**
 * 知识图谱 API
 */

import { request } from './client'
import type { GraphData } from '@/types'

/** 获取图谱数据 */
export function getGraph(): Promise<GraphData> {
  return request<GraphData>('/graph')
}

/** 发现资料关联 */
export function connectMaterial(id: string): Promise<{ connections_found: number; connections_saved: number }> {
  return request(`/ai/connect/${id}`, { method: 'POST' })
}
