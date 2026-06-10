<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores/uiStore'

const route = useRoute()
const ui = useUiStore()

const isDark = ref(document.documentElement.classList.contains('dark'))
function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}
if (localStorage.getItem('theme') === 'dark') document.documentElement.classList.add('dark')

const navItems: {path:string,label:string,icon:string,badge?:string|null}[] = [
  { path: '/', label: '仪表盘', icon: '⊞' },
  { path: '/library', label: '资料库', icon: '⊟' },
  { path: '/graph', label: '知识图谱', icon: '⊠' },
  { path: '/review', label: '复习队列', icon: '⊡' },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <nav class="sidebar flex flex-col z-20" style="width:232px;min-width:232px;height:100vh;background:var(--color-surface);border-right:1px solid var(--color-border)">
    <!-- Brand -->
    <div class="flex items-center gap-2.5 px-4 py-3.5 border-b" style="border-color:var(--color-border);height:48px">
      <div class="w-7 h-7 rounded-[7px] flex items-center justify-center text-[13px] font-bold text-white shrink-0 font-mono"
        style="background:linear-gradient(135deg,var(--color-accent),oklch(58%0.16180));box-shadow:0 0 12px oklch(58%0.16145/0.3)">
        L
      </div>
      <span class="font-semibold text-[15px] tracking-[-0.01em] whitespace-nowrap" style="color:var(--color-fg);font-family:var(--font-sans)">LearnVault</span>
    </div>

    <!-- Nav -->
    <div class="flex-1 p-2 overflow-y-auto">
      <div class="text-xs uppercase tracking-[0.1em] font-semibold px-3 pt-4 pb-2 font-mono" style="color:var(--color-muted)">导航</div>
      <router-link v-for="item in navItems" :key="item.path" :to="item.path"
        class="flex items-center gap-3 px-3 py-3 rounded-[7px] text-sm cursor-pointer transition-colors duration-100 mb-0.5 no-underline"
        :style="isActive(item.path)
          ? { background: 'var(--color-accent-soft)', color: 'var(--color-accent)', fontWeight: '600' }
          : { color: 'var(--color-muted)' }"
      >
        <span class="w-6 h-6 flex items-center justify-center text-base shrink-0">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
        <span v-if="item.badge" class="ml-auto text-[10px] px-1.5 py-px rounded-full font-semibold font-mono"
          style="background:var(--color-accent-soft);color:var(--color-accent)">{{ item.badge }}</span>
      </router-link>
    </div>

    <!-- Footer -->
    <div class="px-3.5 py-2.5 border-t flex items-center gap-1.5 text-[10px] font-mono" style="border-color:var(--color-border);color:var(--color-muted)">
      <span class="w-1.5 h-1.5 rounded-full" style="background:var(--color-accent);box-shadow:0 0 6px var(--color-accent)"></span>
      <span class="flex-1">LearnVault v1.0</span>
      <button @click="toggleDark" class="cursor-pointer border-0 bg-transparent text-sm px-1" style="color:var(--color-muted)">
        {{ isDark ? '☀' : '☾' }}
      </button>
    </div>
  </nav>
</template>
