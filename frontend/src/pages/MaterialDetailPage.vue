<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMaterial, updateMaterial, deleteMaterial } from '@/api/materials'
import { summarizeMaterial, processMaterial } from '@/api/ai'
import { connectMaterial, getGraph } from '@/api/graph'
import { addToReview } from '@/api/review'
import { useWebSocket } from '@/composables/useWebSocket'
import type { Material, GraphEdge } from '@/types'
import TagBadge from '@/components/tags/TagBadge.vue'
import MarkdownRenderer from '@/components/shared/MarkdownRenderer.vue'
import SummaryPanel from '@/components/ai/SummaryPanel.vue'
import AIProcessingIndicator from '@/components/ai/AIProcessingIndicator.vue'

const route = useRoute(); const router = useRouter()
const material = ref<Material | null>(null)
const isEditing = ref(false); const editForm = ref({ title: '', content: '', source: '' })
const loading = ref(true); const error = ref('')
const aiProcessing = ref(false); const aiProgress = ref(0)
const aiMessage = ref(''); const aiStatus = ref<'running'|'completed'|'failed'>('running')
const aiError = ref(''); const currentTaskId = ref('')
const connections = ref<GraphEdge[]>([]); const connectMessage = ref('')
const { lastMessage } = useWebSocket()

watch(lastMessage, (msg) => {
  if (!msg || msg.task_id !== currentTaskId.value) return
  aiProgress.value = msg.progress; aiMessage.value = msg.message; aiStatus.value = msg.status
  if (msg.status === 'failed' && msg.error) aiError.value = msg.error
  if (msg.status === 'completed') setTimeout(() => { aiProcessing.value = false; refreshMaterial() }, 1000)
})

onMounted(() => loadMaterial())

async function loadMaterial() {
  loading.value = true
  try {
    material.value = await getMaterial(route.params.id as string)
    editForm.value = { title: material.value.title, content: material.value.content || '', source: material.value.source || '' }
    error.value = ''; loadConnections()
  } catch { error.value = '资料不存在' } finally { loading.value = false }
}
async function refreshMaterial() { if (!material.value) return; material.value = await getMaterial(material.value.id).catch(() => material.value) }
async function loadConnections() {
  if (!material.value) return
  try { const g = await getGraph(); const mid = material.value.id; connections.value = g.edges.filter((e: any) => e.source === mid || e.target === mid) } catch {}
}

function startEdit() { isEditing.value = true }
async function saveEdit() {
  if (!material.value) return
  try { material.value = await updateMaterial(material.value.id, { title: editForm.value.title, content: editForm.value.content || undefined, source: editForm.value.source || undefined }); isEditing.value = false } catch (e: any) { alert(e.message) }
}
async function handleDelete() { if (!material.value || !confirm('确定删除？')) return; await deleteMaterial(material.value.id); router.push('/library') }

async function handleSummarize() {
  if (!material.value) return; aiProcessing.value = true; aiProgress.value = 0; aiMessage.value = '正在生成摘要...'; aiStatus.value = 'running'; aiError.value = ''
  try { await summarizeMaterial(material.value.id); aiProgress.value = 1; aiMessage.value = '摘要生成完成'; aiStatus.value = 'completed'; setTimeout(() => { aiProcessing.value = false; refreshMaterial() }, 1000) } catch (e: any) { aiStatus.value = 'failed'; aiError.value = e.message; setTimeout(() => aiProcessing.value = false, 3000) }
}
async function handleProcess() {
  if (!material.value) return; aiProcessing.value = true; aiProgress.value = 0; aiMessage.value = '启动 AI 处理...'; aiStatus.value = 'running'; aiError.value = ''
  try { const { task_id } = await processMaterial(material.value.id); currentTaskId.value = task_id } catch (e: any) { aiStatus.value = 'failed'; aiError.value = e.message; setTimeout(() => aiProcessing.value = false, 3000) }
}
async function handleConnect() {
  if (!material.value) return; aiProcessing.value = true; aiStatus.value = 'running'; aiProgress.value = 0.3; aiMessage.value = '正在分析关联...'
  try { const r = await connectMaterial(material.value.id); connectMessage.value = `发现 ${r.connections_found} 条关联`; aiStatus.value = 'completed'; aiProgress.value = 1; await loadConnections(); setTimeout(() => aiProcessing.value = false, 2000) } catch (e: any) { aiStatus.value = 'failed'; aiError.value = e.message; setTimeout(() => aiProcessing.value = false, 3000) }
}
async function handleAddToReview() { if (!material.value) return; try { await addToReview(material.value.id); alert('已加入复习队列') } catch (e: any) { alert(e.message) } }

const typeLabel: Record<string, string> = { note: '📝 笔记', link: '🔗 链接', snippet: '💻 代码片段' }
const relationLabels: Record<string, string> = { prerequisite: '前置', extends: '延伸', related: '相关', contradicts: '矛盾' }
</script>

<template>
  <div v-if="loading" class="text-center py-12" style="color:var(--color-muted)">加载中...</div>
  <div v-else-if="error" class="text-center py-12" style="color:var(--color-danger)">{{ error }}</div>

  <template v-else-if="material">
    <!-- 标题 -->
    <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
      <div>
        <span class="text-sm" style="color:var(--color-muted)">{{ typeLabel[material.type] }}</span>
        <h1 v-if="!isEditing" class="text-[26px] font-bold tracking-[-0.02em] mt-1">{{ material.title }}</h1>
        <input v-else v-model="editForm.title" class="w-full mt-1 px-3.5 py-2 border rounded-[6px] text-lg font-bold" style="border-color:var(--color-border)" />
      </div>
    </div>

    <!-- AI 进度 -->
    <div v-if="aiProcessing" class="mb-6">
      <AIProcessingIndicator :progress="aiProgress" :message="aiMessage" :status="aiStatus" :error="aiError" />
    </div>

    <!-- 工具栏 -->
    <div class="flex items-center gap-2 flex-wrap mb-6 p-4 rounded-[10px] border"
      style="background:var(--color-surface);border-color:var(--color-border)">
      <button v-if="!isEditing" @click="handleSummarize" :disabled="aiProcessing"
        class="btn text-white inline-flex items-center gap-2 px-3 py-1.5 rounded-[6px] text-[13px] font-medium cursor-pointer border transition-all duration-150 disabled:opacity-50"
        style="background:var(--color-accent);border-color:var(--color-accent)">🤖 摘要</button>
      <button v-if="!isEditing" @click="handleProcess" :disabled="aiProcessing"
        class="btn inline-flex items-center gap-2 px-3 py-1.5 rounded-[6px] text-[13px] font-medium cursor-pointer border transition-all duration-150 disabled:opacity-50"
        style="background:var(--color-purple-light);color:var(--color-purple);border-color:transparent">🧠 完整处理</button>
      <button v-if="!isEditing" @click="handleConnect" :disabled="aiProcessing"
        class="btn inline-flex items-center gap-2 px-3 py-1.5 rounded-[6px] text-[13px] font-medium cursor-pointer border transition-all duration-150 disabled:opacity-50"
        style="background:var(--color-success-light);color:#059669;border-color:transparent">🔗 关联</button>
      <button v-if="!isEditing" @click="handleAddToReview"
        class="btn inline-flex items-center gap-2 px-3 py-1.5 rounded-[6px] text-[13px] font-medium cursor-pointer border transition-all duration-150"
        style="background:var(--color-danger-light);color:var(--color-danger);border-color:transparent">📝 复习</button>
      <button v-if="!isEditing" @click="startEdit"
        class="btn ml-auto inline-flex items-center gap-2 px-[18px] py-[9px] rounded-[6px] text-sm font-medium cursor-pointer border transition-all duration-150"
        style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)">编辑</button>
      <button v-else @click="saveEdit"
        class="btn ml-auto inline-flex items-center gap-2 px-[18px] py-[9px] rounded-[6px] text-sm font-medium cursor-pointer border transition-all duration-150 text-white"
        style="background:var(--color-accent);border-color:var(--color-accent)">保存</button>
      <button @click="handleDelete"
        class="btn inline-flex items-center gap-2 px-[18px] py-[9px] rounded-[6px] text-sm font-medium cursor-pointer border transition-all duration-150"
        style="background:var(--color-danger-light);color:var(--color-danger);border-color:transparent">删除</button>
    </div>

    <!-- 元数据 -->
    <div class="grid gap-3 mb-6 p-4 rounded-[10px] border"
      style="background:var(--color-surface);border-color:var(--color-border);grid-template-columns:repeat(auto-fill,minmax(200px,1fr))">
      <div v-if="material.source"><div class="text-[11px] font-semibold uppercase tracking-[0.05em] mb-0.5" style="color:var(--color-muted)">来源</div><div class="text-sm font-medium">{{ material.source }}</div></div>
      <div v-if="material.url"><div class="text-[11px] font-semibold uppercase tracking-[0.05em] mb-0.5" style="color:var(--color-muted)">链接</div><div class="text-sm font-medium"><a :href="material.url ?? undefined" target="_blank" class="truncate block" style="color:var(--color-accent);max-width:400px">{{ (material.url || '').length > 60 ? (material.url || '').slice(0, 60) + '...' : material.url }}</a></div></div>
      <div v-if="material.language"><div class="text-[11px] font-semibold uppercase tracking-[0.05em] mb-0.5" style="color:var(--color-muted)">语言</div><div class="text-sm font-medium">{{ material.language }}</div></div>
      <div><div class="text-[11px] font-semibold uppercase tracking-[0.05em] mb-0.5" style="color:var(--color-muted)">创建</div><div class="text-sm font-medium">{{ new Date(material.created_at).toLocaleString('zh-CN') }}</div></div>
    </div>

    <!-- 标签 -->
    <div class="flex flex-wrap gap-2 mb-6">
      <TagBadge v-for="t in material.tags" :key="t.id" :tag="t" />
      <span v-if="material.tags.length === 0" class="text-sm" style="color:var(--color-muted)">暂无标签</span>
    </div>

    <!-- 摘要 -->
    <div class="mb-6">
      <SummaryPanel :summary="material.summary" :loading="false" />
    </div>

    <!-- 关联 -->
    <div v-if="connections.length > 0" class="mb-6">
      <div class="rounded-[10px] border p-5" style="background:var(--color-surface);border-color:var(--color-border)">
        <h3 class="text-sm font-semibold uppercase tracking-wide mb-3" style="color:var(--color-muted)">🔗 关联资料 ({{ connections.length }})</h3>
        <div class="flex flex-col gap-1.5">
          <div v-for="c in connections.slice(0,5)" :key="c.id" class="flex items-center gap-3 p-2 rounded-[6px] text-sm">
            <span class="text-xs px-2 py-0.5 rounded-full" style="background:#f3f4f6;color:#4b5563">{{ relationLabels[c.relation_type] || c.relation_type }}</span>
            <span class="flex-1 truncate" style="color:var(--color-muted)">{{ c.description }}</span>
            <router-link :to="`/materials/${c.source === material.id ? c.target : c.source}`" style="color:var(--color-accent)" class="hover:underline whitespace-nowrap">查看 →</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 正文 -->
    <div class="rounded-[10px] border p-5" style="background:var(--color-surface);border-color:var(--color-border)">
      <template v-if="!isEditing">
        <MarkdownRenderer v-if="material.content" :content="material.content" />
        <div v-else class="text-sm" style="color:var(--color-muted)">
          <template v-if="material.type === 'link'">链接类型，暂无正文。<a :href="material.url ?? undefined" target="_blank" style="color:var(--color-accent)">打开链接 →</a></template>
          <template v-else>暂无内容</template>
        </div>
      </template>
      <template v-else>
        <label class="block text-[13px] font-semibold mb-1.5" style="color:var(--color-fg)">内容（Markdown）</label>
        <textarea v-model="editForm.content" rows="12" class="form-textarea w-full px-3.5 py-2 border rounded-[6px] text-sm outline-none min-h-[100px] resize-y"
          style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border);font-family:var(--font-mono)" />
        <label class="block text-[13px] font-semibold mt-4 mb-1.5" style="color:var(--color-fg)">来源</label>
        <input v-model="editForm.source" class="w-full px-3.5 py-2 border rounded-[6px] text-sm outline-none"
          style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)" />
      </template>
    </div>
  </template>
</template>
