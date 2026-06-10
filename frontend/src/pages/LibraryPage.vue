<script setup lang="ts">
import { onMounted } from 'vue'
import { useMaterialStore } from '@/stores/materialStore'
import { useUiStore } from '@/stores/uiStore'
import MaterialCard from '@/components/materials/MaterialCard.vue'
import MaterialForm from '@/components/materials/MaterialForm.vue'
import SearchBar from '@/components/shared/SearchBar.vue'

const store = useMaterialStore()
const ui = useUiStore()
onMounted(() => store.fetchMaterials())
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-7 flex-wrap gap-4">
      <div>
        <h1 class="text-[26px] font-bold tracking-[-0.02em]" style="color:var(--color-fg)">资料库</h1>
        <p class="text-sm mt-0.5" style="color:var(--color-muted)">浏览和管理所有学习资料</p>
      </div>
      <button @click="ui.openCreateModal()"
        class="btn inline-flex items-center gap-2 px-[18px] py-[9px] rounded-[6px] text-sm font-medium cursor-pointer border transition-all duration-150 text-white"
        style="background:var(--color-accent);border-color:var(--color-accent)">
        + 添加资料
      </button>
    </div>

    <!-- 工具栏 -->
    <div class="flex items-center gap-3 mb-5 flex-wrap">
      <SearchBar :value="store.filters.search" @search="(v: string) => store.setFilter('search', v)" />
      <select :value="store.filters.type" @change="store.setFilter('type', ($event.target as HTMLSelectElement).value)"
        class="filter-select px-3.5 py-[9px] border rounded-[6px] text-sm cursor-pointer outline-none"
        style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)">
        <option value="">全部类型</option>
        <option value="note">📝 笔记</option>
        <option value="link">🔗 链接</option>
        <option value="snippet">💻 代码片段</option>
      </select>
    </div>

    <!-- 列表 -->
    <div v-if="store.loading" class="text-center py-12" style="color:var(--color-muted)">加载中...</div>
    <div v-else-if="store.materials.length === 0" class="text-center py-12" style="color:var(--color-muted)">
      暂无资料，点击「添加资料」开始
    </div>
    <div v-else class="flex flex-col gap-2.5">
      <MaterialCard v-for="m in store.materials" :key="m.id" :material="m" />
    </div>

    <!-- 分页 -->
    <div v-if="store.total > store.filters.pageSize" class="flex items-center justify-center gap-1.5 mt-6">
      <button v-for="p in Math.ceil(store.total / store.filters.pageSize)" :key="p"
        class="w-9 h-9 border rounded-[6px] text-[13px] grid place-items-center cursor-pointer transition-all duration-150"
        :style="p === store.filters.page
          ? { background: 'var(--color-accent)', color: '#fff', borderColor: 'var(--color-accent)' }
          : { background: 'var(--color-surface)', color: 'var(--color-fg)', borderColor: 'var(--color-border)' }"
        @click="store.setPage(p)">{{ p }}</button>
    </div>

    <MaterialForm v-if="ui.showCreateModal" @close="ui.closeCreateModal()" />
  </div>
</template>
