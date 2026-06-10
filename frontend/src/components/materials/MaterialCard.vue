<script setup lang="ts">
import type { Material } from '@/types'
defineProps<{ material: Material }>()
const typeLabel: Record<string, string> = { note: '笔记', link: '链接', snippet: '代码片段' }
const typeColor: Record<string, string> = { note: 'var(--color-info)', link: 'var(--color-warn)', snippet: 'var(--color-accent)' }
</script>
<template>
  <router-link :to="`/materials/${material.id}`"
    class="card block rounded-[10px] border p-[18px] no-underline transition-shadow duration-150 hover:shadow-sm"
    style="background:var(--color-surface);border-color:var(--color-border)">
    <div class="flex items-start justify-between mb-3">
      <div class="flex-1 min-w-0">
        <div class="font-semibold text-[13.5px] tracking-[-0.005em] mb-1" style="color:var(--color-fg)">{{ material.title }}</div>
        <div class="text-[12px] line-clamp-1" style="color:var(--color-muted)">
          {{ material.content || material.url || '无内容' }}
        </div>
      </div>
      <span class="text-[11px] font-mono whitespace-nowrap ml-3" style="color:var(--color-muted)">{{ new Date(material.created_at).toLocaleDateString('zh-CN') }}</span>
    </div>
    <div class="flex items-center gap-2 flex-wrap">
      <span class="text-[10.5px] font-semibold px-2 py-0.5 rounded-md font-mono tracking-[0.04em]"
        :style="{background:typeColor[material.type]+'18',color:typeColor[material.type]}">
        {{ typeLabel[material.type] }}
      </span>
      <template v-for="t in material.tags.slice(0,3)" :key="t.id">
        <span class="text-[10.5px] px-2 py-0.5 rounded-full font-medium" style="background:var(--color-bg);color:var(--color-muted)">{{ t.name }}</span>
      </template>
      <span v-if="!material.is_processed" class="text-[10.5px] font-semibold px-2 py-0.5 rounded-full font-mono tracking-[0.04em]"
        style="background:var(--color-warn-soft);color:var(--color-warn)">待处理</span>
    </div>
  </router-link>
</template>
