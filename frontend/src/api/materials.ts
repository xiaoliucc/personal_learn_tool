/**
 * 资料 API 调用
 */

import { request } from './client'
import type {
  Material,
  MaterialCreate,
  MaterialUpdate,
  MaterialListResponse,
} from '@/types'

/** 获取资料列表 */
export function getMaterials(params?: {
  page?: number
  page_size?: number
  type?: string
  tag?: string
  search?: string
}): Promise<MaterialListResponse> {
  const searchParams = new URLSearchParams()
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        searchParams.set(key, String(value))
      }
    })
  }
  const query = searchParams.toString()
  return request<MaterialListResponse>(`/materials${query ? `?${query}` : ''}`)
}

/** 获取资料详情 */
export function getMaterial(id: string): Promise<Material> {
  return request<Material>(`/materials/${id}`)
}

/** 创建资料 */
export function createMaterial(data: MaterialCreate): Promise<Material> {
  return request<Material>('/materials', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/** 更新资料 */
export function updateMaterial(id: string, data: MaterialUpdate): Promise<Material> {
  return request<Material>(`/materials/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/** 删除资料 */
export function deleteMaterial(id: string): Promise<void> {
  return request<void>(`/materials/${id}`, { method: 'DELETE' })
}
