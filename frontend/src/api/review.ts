/** 复习 API */
import { request } from './client'

export interface ReviewItem {
  id: string
  material_id: string
  material_title: string
  ease_factor: number
  interval: number
  repetitions: number
  next_review_at: string | null
}

export function getDueReviews(): Promise<ReviewItem[]> {
  return request<ReviewItem[]>('/review/due')
}

export function getDueCount(): Promise<{ count: number }> {
  return request<{ count: number }>('/review/due/count')
}

export function addToReview(materialId: string): Promise<any> {
  return request(`/review/add/${materialId}`, { method: 'POST' })
}

export function recordReview(reviewId: string, quality: number): Promise<any> {
  return request(`/review/record/${reviewId}?quality=${quality}`, { method: 'POST' })
}
