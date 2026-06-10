<script setup lang="ts">
/**
 * Markdown 渲染组件
 *
 * 使用 markdown-it 完整支持 Markdown 语法：
 * - 标题、列表、粗体、链接、图片
 * - 表格（GFM）
 * - 代码块 + 行内代码
 * - 引用块、分隔线
 */

import MarkdownIt from 'markdown-it'

defineProps<{ content: string }>()

const md = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: true,
  typographer: true,
})

function renderMarkdown(text: string): string {
  if (!text) return ''
  return md.render(text)
}
</script>

<template>
  <div
    class="markdown-body"
    v-html="renderMarkdown(content)"
  />
</template>

<style>
/* Markdown 渲染样式 — 全局作用，确保 v-html 内容也被覆盖 */
.markdown-body {
  color: #374151;
  line-height: 1.75;
  word-break: break-word;
}

/* 标题 */
.markdown-body h1 { font-size: 1.5rem; font-weight: 700; color: #1f2937; margin: 1.5rem 0 0.75rem; }
.markdown-body h2 { font-size: 1.25rem; font-weight: 600; color: #1f2937; margin: 1.25rem 0 0.5rem; }
.markdown-body h3 { font-size: 1.1rem; font-weight: 600; color: #1f2937; margin: 1rem 0 0.5rem; }
.markdown-body h4 { font-size: 1rem; font-weight: 600; color: #374151; margin: 0.75rem 0 0.25rem; }

/* 段落 */
.markdown-body p { margin: 0.5rem 0; }

/* 列表 */
.markdown-body ul,
.markdown-body ol { padding-left: 1.5rem; margin: 0.5rem 0; }
.markdown-body li { margin: 0.25rem 0; }
.markdown-body ul { list-style-type: disc; }
.markdown-body ol { list-style-type: decimal; }
.markdown-body li > ul,
.markdown-body li > ol { margin: 0; }

/* 链接 */
.markdown-body a { color: #2563eb; text-decoration: underline; }
.markdown-body a:hover { color: #1d4ed8; }

/* 行内代码 */
.markdown-body code {
  background: #f3f4f6;
  color: #dc2626;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: ui-monospace, Consolas, monospace;
}

/* 代码块 */
.markdown-body pre {
  background: #1f2937;
  color: #86efac;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0.75rem 0;
  font-size: 0.875rem;
  line-height: 1.6;
}
.markdown-body pre code {
  background: none;
  color: inherit;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

/* 表格 */
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
  font-size: 0.875rem;
}
.markdown-body th {
  background: #f3f4f6;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  text-align: left;
}
.markdown-body td {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
}
.markdown-body tr:nth-child(even) td { background: #f9fafb; }

/* 引用块 */
.markdown-body blockquote {
  border-left: 4px solid #93c5fd;
  background: #eff6ff;
  padding: 0.5rem 1rem;
  margin: 0.75rem 0;
  color: #475569;
}

/* 分隔线 */
.markdown-body hr { border: none; border-top: 2px solid #e5e7eb; margin: 1rem 0; }

/* 粗体/斜体 */
.markdown-body strong { font-weight: 600; color: #1f2937; }
.markdown-body em { font-style: italic; }

/* 图片 */
.markdown-body img { max-width: 100%; border-radius: 0.5rem; margin: 0.5rem 0; }

/* 删除线 */
.markdown-body del { text-decoration: line-through; color: #9ca3af; }
</style>
