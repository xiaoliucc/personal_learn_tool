/**
 * 标签 API 调用
 */

import { request } from './client'
import type { Tag, TagCreate, TagUpdate } from '@/types'

/** 获取所有标签（树形结构） */
export function getTags(): Promise<Tag[]> {
  return request<Tag[]>('/tags')
}

/** 创建标签 */
export function createTag(data: TagCreate): Promise<Tag> {
  return request<Tag>('/tags', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/** 更新标签 */
export function updateTag(id: string, data: TagUpdate): Promise<Tag> {
  return request<Tag>(`/tags/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/** 删除标签 */
export function deleteTag(id: string): Promise<void> {
  return request<void>(`/tags/${id}`, { method: 'DELETE' })
}
