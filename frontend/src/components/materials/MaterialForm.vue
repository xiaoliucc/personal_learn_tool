<script setup lang="ts">
import { ref } from 'vue'
import { createMaterial } from '@/api/materials'
import { useMaterialStore } from '@/stores/materialStore'
import type { MaterialType } from '@/types'
const emit = defineEmits<{ close: [] }>()
const store = useMaterialStore()
const form = ref({ type: 'note' as MaterialType, title: '', content: '', url: '', language: '', source: '' })
const submitting = ref(false)
const error = ref('')
async function submit() {
  if (!form.value.title.trim()) { error.value = '标题不能为空'; return }
  submitting.value = true; error.value = ''
  try {
    await createMaterial({ type: form.value.type, title: form.value.title.trim(),
      content: form.value.content.trim() || undefined, url: form.value.url.trim() || undefined,
      language: form.value.language.trim() || undefined, source: form.value.source.trim() || undefined })
    store.fetchMaterials(); emit('close')
  } catch (e: any) { error.value = e.message } finally { submitting.value = false }
}
</script>
<template>
  <div class="modal-overlay fixed inset-0 flex items-center justify-center z-[1000]"
    style="background:rgba(0,0,0,0.45);backdrop-filter:blur(2px)" @click.self="emit('close')">
    <div class="w-[90%] max-w-[560px] max-h-[85vh] overflow-y-auto rounded-[14px] p-7"
      style="background:var(--color-surface);box-shadow:0 25px 60px rgba(0,0,0,0.2)">
      <h2 class="text-xl font-bold mb-6 tracking-[-0.01em]">添加资料</h2>
      <div v-if="error" class="mb-4 p-3 rounded-[6px] text-sm" style="background:var(--color-danger-light);color:var(--color-danger)">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="mb-[18px]">
          <label class="block text-[13px] font-semibold mb-1.5" style="color:var(--color-fg)">类型</label>
          <select v-model="form.type" class="w-full px-3.5 py-[9px] border rounded-[6px] text-sm outline-none transition-colors duration-150"
            style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)">
            <option value="note">📝 笔记</option>
            <option value="link">🔗 链接</option>
            <option value="snippet">💻 代码片段</option>
          </select>
        </div>
        <div class="mb-[18px]">
          <label class="block text-[13px] font-semibold mb-1.5" style="color:var(--color-fg)">标题 *</label>
          <input v-model="form.title" class="w-full px-3.5 py-[9px] border rounded-[6px] text-sm outline-none transition-colors duration-150"
            style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)" placeholder="输入资料标题" />
        </div>
        <div v-if="form.type === 'link'" class="mb-[18px]">
          <label class="block text-[13px] font-semibold mb-1.5" style="color:var(--color-fg)">URL</label>
          <input v-model="form.url" type="url" class="w-full px-3.5 py-[9px] border rounded-[6px] text-sm outline-none transition-colors duration-150"
            style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)" placeholder="https://..." />
        </div>
        <div v-if="form.type === 'snippet'" class="mb-[18px]">
          <label class="block text-[13px] font-semibold mb-1.5" style="color:var(--color-fg)">编程语言</label>
          <input v-model="form.language" class="w-full px-3.5 py-[9px] border rounded-[6px] text-sm outline-none transition-colors duration-150"
            style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)" placeholder="python / typescript / ..." />
        </div>
        <div v-if="form.type !== 'link'" class="mb-[18px]">
          <label class="block text-[13px] font-semibold mb-1.5" style="color:var(--color-fg)">内容（Markdown）</label>
          <textarea v-model="form.content" rows="6" class="form-textarea w-full px-3.5 py-[9px] border rounded-[6px] text-sm outline-none transition-colors duration-150 min-h-[100px] resize-y"
            style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border);font-family:var(--font-mono)" />
        </div>
        <div class="mb-[18px]">
          <label class="block text-[13px] font-semibold mb-1.5" style="color:var(--color-fg)">来源（可选）</label>
          <input v-model="form.source" class="w-full px-3.5 py-[9px] border rounded-[6px] text-sm outline-none transition-colors duration-150"
            style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)" placeholder="书名 / 课程 / 作者..." />
        </div>
        <div class="flex justify-end gap-2.5 mt-6">
          <button type="button" @click="emit('close')"
            class="btn inline-flex items-center gap-2 px-[18px] py-[9px] rounded-[6px] text-sm font-medium cursor-pointer border transition-all duration-150"
            style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)">取消</button>
          <button type="submit" :disabled="submitting"
            class="btn inline-flex items-center gap-2 px-[18px] py-[9px] rounded-[6px] text-sm font-medium cursor-pointer border transition-all duration-150 text-white disabled:opacity-50"
            style="background:var(--color-accent);border-color:var(--color-accent)">
            {{ submitting ? '创建中...' : '创建' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
