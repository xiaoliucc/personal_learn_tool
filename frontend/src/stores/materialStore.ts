/**
 * 资料 Store — 管理资料列表、筛选、当前选中资料
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMaterials, getMaterial } from '@/api/materials'
import type { Material, MaterialType } from '@/types'

export const useMaterialStore = defineStore('material', () => {
  // ---- 状态 ----
  const materials = ref<Material[]>([])
  const currentMaterial = ref<Material | null>(null)
  const total = ref(0)
  const loading = ref(false)

  // 筛选条件
  const filters = ref({
    page: 1,
    pageSize: 20,
    type: '' as MaterialType | '',
    tag: '',
    search: '',
  })

  // ---- 操作 ----
  async function fetchMaterials() {
    loading.value = true
    try {
      const res = await getMaterials({
        page: filters.value.page,
        page_size: filters.value.pageSize,
        type: filters.value.type || undefined,
        tag: filters.value.tag || undefined,
        search: filters.value.search || undefined,
      })
      materials.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchMaterial(id: string) {
    loading.value = true
    try {
      currentMaterial.value = await getMaterial(id)
    } finally {
      loading.value = false
    }
  }

  function setFilter(key: string, value: string | number) {
    filters.value = { ...filters.value, [key]: value, page: 1 }
    fetchMaterials()
  }

  function setPage(page: number) {
    filters.value.page = page
    fetchMaterials()
  }

  return {
    materials,
    currentMaterial,
    total,
    loading,
    filters,
    fetchMaterials,
    fetchMaterial,
    setFilter,
    setPage,
  }
})
