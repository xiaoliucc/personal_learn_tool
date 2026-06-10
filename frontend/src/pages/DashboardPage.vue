<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMaterials } from '@/api/materials'
import { getDueCount } from '@/api/review'

const stats = ref({ total: 0, notes: 0, links: 0, snippets: 0, dueReviews: 0 })
const recent = ref<any[]>([])
const activity = ref<any[]>([])

onMounted(async () => {
  const [all, notes, links, snippets, due] = await Promise.all([
    getMaterials({ page_size: 1 }),
    getMaterials({ type: 'note', page_size: 1 }),
    getMaterials({ type: 'link', page_size: 1 }),
    getMaterials({ type: 'snippet', page_size: 1 }),
    getDueCount().catch(() => ({ count: 0 })),
  ])
  stats.value = { total: all.total, notes: notes.total, links: links.total, snippets: snippets.total, dueReviews: due.count }
  const r = await getMaterials({ page_size: 6 })
  recent.value = r.items
  activity.value = r.items.slice(0, 6).map(m => ({
    color: m.type === 'note' ? 'var(--color-info)' : m.type === 'link' ? 'var(--color-warn)' : 'var(--color-accent)',
    title: m.title.length > 28 ? m.title.slice(0,28)+'...' : m.title,
    time: new Date(m.created_at).toLocaleDateString('zh-CN')
  }))
})

const typeIcon: Record<string, string> = { note: '📄', link: '🔗', snippet: '⌨' }
</script>

<template>
  <div>
    <!-- Stats -->
    <div class="grid gap-3 mb-5" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr))">
      <div v-for="s in [
        {label:'资料总数',v:stats.total,icon:'⊞',color:'var(--color-fg)'},
        {label:'笔记',v:stats.notes,icon:'📄',color:'var(--color-info)'},
        {label:'链接',v:stats.links,icon:'🔗',color:'var(--color-warn)'},
        {label:'代码片段',v:stats.snippets,icon:'⌨',color:'var(--color-accent)'},
        {label:'待复习',v:stats.dueReviews,icon:'⊡',color:'var(--color-danger)'}
      ]" :key="s.label" class="card rounded-[10px] border p-4"
        style="background:var(--color-surface);border-color:var(--color-border)">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[11px] font-semibold uppercase tracking-[0.06em] font-mono" style="color:var(--color-muted)">{{ s.label }}</span>
          <span style="color:var(--color-muted);font-size:14px">{{ s.icon }}</span>
        </div>
        <div class="text-[28px] font-bold tracking-[-0.03em] tabular-nums font-sans" :style="{color:s.color}">{{ s.v }}</div>
      </div>
    </div>

    <!-- Activity + Export -->
    <div class="grid gap-5" style="grid-template-columns:1fr 320px">
      <!-- Recent activity -->
      <div class="card rounded-[10px] border p-5" style="background:var(--color-surface);border-color:var(--color-border)">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-[13.5px] font-semibold font-sans tracking-[-0.005em]" style="color:var(--color-fg)">最近动态</h3>
        </div>
        <div class="space-y-2">
          <div v-for="(a,i) in activity" :key="i" class="flex items-center gap-3 py-1.5">
            <span class="w-2 h-2 rounded-full shrink-0" :style="{background:a.color}"></span>
            <span class="text-[12.5px] flex-1 truncate" style="color:var(--color-fg)">{{ a.title }}</span>
            <span class="text-[11px] font-mono whitespace-nowrap" style="color:var(--color-muted)">{{ a.time }}</span>
          </div>
          <div v-if="!activity.length" class="text-xs text-center py-6" style="color:var(--color-muted)">暂无动态</div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="space-y-5">
        <div class="card rounded-[10px] border p-5" style="background:var(--color-surface);border-color:var(--color-border)">
          <h3 class="text-[13.5px] font-semibold mb-3 font-sans">快捷操作</h3>
          <a href="/api/export/json" target="_blank" class="block text-[12px] py-1.5 no-underline" style="color:var(--color-muted)">📦 JSON 导出</a>
          <a href="/api/export/markdown" target="_blank" class="block text-[12px] py-1.5 no-underline" style="color:var(--color-muted)">📝 Markdown 导出</a>
        </div>
        <div class="card rounded-[10px] border p-5" style="background:var(--color-surface);border-color:var(--color-border)">
          <h3 class="text-[13.5px] font-semibold mb-3 font-sans">最近资料</h3>
          <div class="space-y-2">
            <router-link v-for="m in recent.slice(0,5)" :key="m.id" :to="`/materials/${m.id}`"
              class="flex items-center gap-2 text-[12px] no-underline py-0.5 truncate" style="color:var(--color-fg)">
              <span>{{ typeIcon[m.type] || '📄' }}</span>
              <span class="truncate">{{ m.title }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
