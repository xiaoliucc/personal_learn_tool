<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{ value: string }>()
const emit = defineEmits<{ search: [value: string] }>()
const local = ref(props.value)
let t: any = null
watch(local, (v) => { clearTimeout(t); t = setTimeout(() => emit('search', v), 300) })
watch(() => props.value, (v) => { local.value = v })
</script>
<template>
  <div class="relative flex-1 min-w-[200px]" style="max-width:420px">
    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[15px]" style="color:var(--color-muted)">🔍</span>
    <input v-model="local" type="text" placeholder="搜索资料..."
      class="w-full pl-[38px] pr-3.5 py-[9px] border rounded-[6px] text-sm outline-none transition-colors duration-150"
      style="background:var(--color-surface);color:var(--color-fg);border-color:var(--color-border)"
    />
  </div>
</template>
