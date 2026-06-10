<script setup lang="ts">
/**
 * 知识图谱页面
 *
 * 使用 vis-network 绘制力导向图：
 * - 节点 = 学习资料（按类型着色）
 * - 边 = AI 发现的关联（按类型标注）
 * - 点击节点跳转资料详情
 */
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getGraph } from '@/api/graph'
import type { GraphData } from '@/types'

const router = useRouter()
const graphData = ref<GraphData | null>(null)
const loading = ref(true)
const containerRef = ref<HTMLElement | null>(null)
let network: any = null

// 类型对应的颜色
const typeColors: Record<string, string> = {
  note: '#3b82f6',
  link: '#f59e0b',
  snippet: '#8b5cf6',
}

// 关联类型的中文标签
const relationLabels: Record<string, string> = {
  prerequisite: '前置',
  extends: '延伸',
  related: '相关',
  contradicts: '矛盾',
}

onMounted(async () => {
  try {
    graphData.value = await getGraph()
  } catch {
    graphData.value = { nodes: [], edges: [] }
  } finally {
    loading.value = false
    await nextTick()
    if (graphData.value && graphData.value.nodes.length > 0) {
      renderGraph()
    }
  }
})

onUnmounted(() => {
  if (network) network.destroy()
})

async function renderGraph() {
  if (!containerRef.value || !graphData.value) return

  // 动态导入 vis-network（避免 SSR 问题）
  const { Network } = await import('vis-network') as any

  const nodes = graphData.value.nodes.map((n) => ({
    id: n.id,
    label: n.title.length > 15 ? n.title.slice(0, 15) + '...' : n.title,
    title: `<b>${n.title}</b><br>类型：${n.type}`,
    color: {
      background: typeColors[n.type] || '#6b7280',
      border: typeColors[n.type],
      highlight: { background: typeColors[n.type], border: '#1e293b' },
    },
    font: { color: '#1e293b', size: 14, face: 'system-ui' },
    shape: 'box',
    size: 25,
    borderWidth: 2,
    borderWidthSelected: 4,
    margin: { top: 8, right: 12, bottom: 8, left: 12 },
  }))

  const edges = graphData.value.edges.map((e) => ({
    id: e.id,
    from: e.source,
    to: e.target,
    label: relationLabels[e.relation_type] || e.relation_type,
    title: e.description || '',
    color: { color: '#cbd5e1', highlight: '#6366f1' },
    width: Math.max(1, e.strength * 3),
    arrows: 'to',
    smooth: { type: 'continuous' },
  }))

  const options = {
    physics: {
      stabilization: { iterations: 100 },
      barnesHut: { gravitationalConstant: -2000, springLength: 200 },
    },
    interaction: {
      hover: true,
      tooltipDelay: 0,    // 禁用内置 tooltip（避免 DOM 操作破坏布局）
      zoomView: true,
      dragView: true,
    },
    edges: {
      font: { size: 10, color: '#64748b', background: '#fff' },
    },
  }

  network = new Network(containerRef.value, { nodes, edges }, options)

  // 点击节点跳转
  network.on('click', function (params: any) {
    if (params.nodes.length > 0) {
      router.push(`/materials/${params.nodes[0]}`)
    }
  })
}
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">知识图谱</h1>

    <!-- 加载 -->
    <div v-if="loading" class="flex items-center justify-center text-gray-400" style="height: 400px">
      加载图谱数据...
    </div>

    <!-- 空状态 -->
    <div v-else-if="!graphData || graphData.nodes.length === 0"
      class="flex items-center justify-center" style="height: 400px">
      <div class="text-center text-gray-400">
        <div class="text-5xl mb-4">🔗</div>
        <p class="text-lg">还没有知识关联</p>
        <p class="text-sm mt-2">
          在资料详情页点击「发现关联」，AI 会自动分析资料间的关系
        </p>
      </div>
    </div>

    <!-- 图例 -->
    <div v-if="graphData && graphData.nodes.length > 0" class="flex gap-4 mb-4 text-sm">
      <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-blue-500 inline-block"></span> 笔记</span>
      <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-amber-500 inline-block"></span> 链接</span>
      <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-purple-500 inline-block"></span> 代码片段</span>
    </div>

    <!-- 图谱容器 — 显式高度，避免 vis-network tooltip 导致 flex 布局崩溃 -->
    <div
      v-if="graphData && graphData.nodes.length > 0"
      ref="containerRef"
      class="bg-white rounded-xl shadow-sm border border-gray-100"
      style="height: calc(100vh - 240px); min-height: 400px"
    />
  </div>
</template>
