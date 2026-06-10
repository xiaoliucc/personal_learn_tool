<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

/** 面包屑映射 */
const breadcrumb: Record<string, string> = {
  '/': '仪表盘',
  '/library': '资料库',
  '/graph': '知识图谱',
  '/review': '复习队列',
}
const title = breadcrumb[route.path] || (route.path.startsWith('/materials/') ? '资料详情' : '')
</script>

<template>
  <header class="flex items-center justify-between px-5 h-12 border-b shrink-0" style="background:var(--color-surface);border-color:var(--color-border);min-height:48px">
    <div class="flex items-center gap-3">
      <span class="text-xs" style="color:var(--color-muted)">{{ title }}</span>
    </div>
    <div class="flex items-center gap-3.5">
      <!-- Global search -->
      <div class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-[7px] border" style="background:var(--color-bg);border-color:var(--color-border)">
        <span class="text-xs" style="color:var(--color-muted)">⌕</span>
        <input placeholder="搜索..." class="border-0 bg-transparent outline-none text-xs w-40 font-sans" style="color:var(--color-fg)" />
      </div>
    </div>
  </header>
</template>
