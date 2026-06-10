<script setup lang="ts">
import type { TagBrief } from '@/types'
defineProps<{ tag: TagBrief }>()
</script>
<template>
  <span class="inline-flex items-center gap-1 px-2.5 py-[3px] rounded-full text-xs font-medium whitespace-nowrap"
    :style="{ background: (tag.color || '#3b82f6') + '18', color: tag.color || '#3b82f6' }"
  >
    {{ tag.name }}
    <span v-if="tag.confidence !== null && tag.confidence < 1" class="opacity-60 text-[10px]">
      {{ Math.round(tag.confidence * 100) }}%
    </span>
  </span>
</template>
