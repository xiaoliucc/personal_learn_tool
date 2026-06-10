<script setup lang="ts">
/**
 * AI 处理进度指示器
 *
 * 显示 AI 处理的实时进度条和状态消息。
 * 通过 props 接收进度信息，也可绑定 WebSocket 消息。
 */

defineProps<{
  progress: number     // 0.0 ~ 1.0
  message: string      // 当前状态描述
  status: 'running' | 'completed' | 'failed'
  error?: string
}>()
</script>

<template>
  <div
    class="rounded-lg border p-4 transition-colors"
    :class="{
      'border-blue-200 bg-blue-50': status === 'running',
      'border-green-200 bg-green-50': status === 'completed',
      'border-red-200 bg-red-50': status === 'failed',
    }"
  >
    <!-- 进度条 -->
    <div class="flex items-center gap-3 mb-2">
      <!-- 图标 -->
      <span v-if="status === 'running'" class="text-blue-500 animate-spin text-lg">⏳</span>
      <span v-else-if="status === 'completed'" class="text-green-500 text-lg">✅</span>
      <span v-else class="text-red-500 text-lg">❌</span>

      <!-- 状态文字 -->
      <span class="text-sm font-medium" :class="{
        'text-blue-700': status === 'running',
        'text-green-700': status === 'completed',
        'text-red-700': status === 'failed',
      }">
        {{ message }}
      </span>

      <!-- 百分比 -->
      <span class="ml-auto text-xs text-gray-500">
        {{ Math.round(progress * 100) }}%
      </span>
    </div>

    <!-- 进度条 -->
    <div class="w-full bg-gray-200 rounded-full h-1.5">
      <div
        class="h-1.5 rounded-full transition-all duration-500"
        :class="{
          'bg-blue-500': status === 'running',
          'bg-green-500': status === 'completed',
          'bg-red-500': status === 'failed',
        }"
        :style="{ width: `${progress * 100}%` }"
      />
    </div>

    <!-- 错误详情 -->
    <p v-if="error" class="mt-2 text-xs text-red-600">{{ error }}</p>
  </div>
</template>
