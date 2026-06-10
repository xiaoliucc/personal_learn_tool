/**
 * AI API 调用
 */

import { request } from './client'

/** AI 分类结果 */
export interface ClassifyResult {
  tags: Array<{ name: string; confidence: number; color: string }>
}

/** AI 摘要结果 */
export interface SummarizeResult {
  summary: string
  key_points: string[]
}

/** AI 处理任务 */
export interface ProcessTask {
  task_id: string
  message: string
}

/** 对资料进行 AI 分类 */
export function classifyMaterial(id: string): Promise<ClassifyResult> {
  return request<ClassifyResult>(`/ai/classify/${id}`, { method: 'POST' })
}

/** 生成 AI 摘要 */
export function summarizeMaterial(id: string): Promise<SummarizeResult> {
  return request<SummarizeResult>(`/ai/summarize/${id}`, { method: 'POST' })
}

/** 触发完整 AI 处理 */
export function processMaterial(id: string): Promise<ProcessTask> {
  return request<ProcessTask>(`/ai/process/${id}`, { method: 'POST' })
}
