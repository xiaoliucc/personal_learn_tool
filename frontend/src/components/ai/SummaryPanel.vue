<script setup lang="ts">
/**
 * AI 摘要面板
 *
 * 展示 AI 生成的资料摘要和关键要点。
 * 如果 summary 为 null，显示"尚未生成摘要"。
 */

defineProps<{
  summary: {
    content: string
    key_points?: string[] | null
    model_used?: string | null
    generated_at?: string | null
  } | null
  loading?: boolean
}>()
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
    <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
      🤖 AI 摘要
    </h3>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center text-gray-400 py-4">
      <span class="animate-spin inline-block mr-2">⏳</span> AI 正在生成摘要...
    </div>

    <!-- 无摘要 -->
    <div v-else-if="!summary" class="text-center text-gray-400 py-4 text-sm">
      尚未生成摘要，点击工具栏「生成摘要」让 AI 帮你总结
    </div>

    <!-- 摘要内容 -->
    <template v-else>
      <p class="text-sm text-gray-700 leading-relaxed mb-4">{{ summary.content }}</p>

      <!-- 关键要点 -->
      <div v-if="summary.key_points && summary.key_points.length > 0" class="mb-3">
        <h4 class="text-xs font-semibold text-gray-400 uppercase mb-2">关键要点</h4>
        <ul class="space-y-1.5">
          <li
            v-for="(point, i) in summary.key_points"
            :key="i"
            class="flex items-start gap-2 text-sm text-gray-600"
          >
            <span class="text-blue-400 mt-0.5">•</span>
            {{ point }}
          </li>
        </ul>
      </div>

      <!-- 元数据 -->
      <div class="flex items-center gap-3 text-xs text-gray-400 mt-3 pt-3 border-t border-gray-100">
        <span v-if="summary.model_used">模型：{{ summary.model_used }}</span>
        <span v-if="summary.generated_at">
          生成于 {{ new Date(summary.generated_at).toLocaleString('zh-CN') }}
        </span>
      </div>
    </template>
  </div>
</template>
