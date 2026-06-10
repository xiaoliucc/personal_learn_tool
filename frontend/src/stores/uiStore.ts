/**
 * UI Store — 侧边栏、弹窗等界面状态
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const sidebarCollapsed = ref(false)
  const showCreateModal = ref(false)
  const showEditModal = ref(false)

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function openCreateModal() {
    showCreateModal.value = true
  }

  function closeCreateModal() {
    showCreateModal.value = false
  }

  return {
    sidebarCollapsed,
    showCreateModal,
    showEditModal,
    toggleSidebar,
    openCreateModal,
    closeCreateModal,
  }
})
