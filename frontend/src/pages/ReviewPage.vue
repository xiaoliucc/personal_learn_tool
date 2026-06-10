<script setup lang="ts">
/**
 * 复习页 — SM-2 间隔重复卡片
 */
import { ref, onMounted, computed, watch } from 'vue'
import { getDueReviews, recordReview } from '@/api/review'
import { getMaterial } from '@/api/materials'
import type { ReviewItem } from '@/api/review'
import MarkdownRenderer from '@/components/shared/MarkdownRenderer.vue'

const items = ref<ReviewItem[]>([])
const currentIndex = ref(0)
const loading = ref(true)
const showContent = ref(false)
const message = ref('')

onMounted(async () => {
  await loadReviews()
})

async function loadReviews() {
  loading.value = true
  try {
    items.value = await getDueReviews()
  } catch { items.value = [] }
  finally { loading.value = false }
}

const current = computed(() => items.value[currentIndex.value] || null)

async function rate(quality: number) {
  if (!current.value) return
  try {
    await recordReview(current.value.id, quality)
    message.value = quality >= 3 ? '✅ 已记录' : '🔄 需要重新复习'
    setTimeout(() => {
      message.value = ''
      currentIndex.value++
      showContent.value = false
      if (currentIndex.value >= items.value.length) {
        items.value = []
        currentIndex.value = 0
      }
    }, 600)
  } catch (e: any) {
    message.value = `错误：${e.message}`
  }
}

// 加载资料内容（按需）
const materialContent = ref('')
watch(current, async (item) => {
  if (!item) { materialContent.value = ''; return }
  try {
    const m = await getMaterial(item.material_id)
    materialContent.value = m.content || ''
  } catch { materialContent.value = '' }
})
</script>

<template>
  <div class="p-8 max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">📝 复习</h1>

    <!-- 加载 -->
    <div v-if="loading" class="text-center text-gray-400 py-12">加载中...</div>

    <!-- 全部完成 -->
    <div v-else-if="items.length === 0 || currentIndex >= items.length"
      class="text-center py-12">
      <div class="text-5xl mb-4">🎉</div>
      <p class="text-lg text-gray-600">今日复习全部完成！</p>
      <p class="text-sm text-gray-400 mt-2">在资料详情页点击「加入复习」添加更多</p>
    </div>

    <!-- 复习卡片 -->
    <div v-else-if="current" class="space-y-6">
      <!-- 进度 -->
      <div class="text-sm text-gray-400">
        {{ currentIndex + 1 }} / {{ items.length }}
      </div>

      <!-- 卡片 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <h2 class="text-xl font-bold text-gray-800 mb-4">{{ current.material_title }}</h2>

        <!-- SM-2 元数据 -->
        <div class="flex gap-4 text-xs text-gray-400 mb-4">
          <span>间隔：{{ current.interval }} 天</span>
          <span>复习次数：{{ current.repetitions }}</span>
        </div>

        <!-- 内容（可展开） -->
        <div v-if="!showContent" class="text-center py-8">
          <button
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            @click="showContent = true"
          >
            显示内容
          </button>
        </div>
        <div v-else class="border-t pt-4">
          <MarkdownRenderer v-if="materialContent" :content="materialContent" />
          <div v-else class="text-gray-400 text-sm">无内容</div>
        </div>
      </div>

      <!-- 评分按钮 -->
      <div v-if="showContent" class="flex justify-center gap-3 flex-wrap">
        <button @click="rate(0)" class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm">
          😫 完全忘了 (0)
        </button>
        <button @click="rate(2)" class="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 text-sm">
          🤔 模糊 (2)
        </button>
        <button @click="rate(3)" class="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 text-sm">
          🙂 勉强记得 (3)
        </button>
        <button @click="rate(4)" class="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 text-sm">
          😊 较熟悉 (4)
        </button>
        <button @click="rate(5)" class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-sm">
          🎯 完美 (5)
        </button>
      </div>

      <!-- 消息 -->
      <div v-if="message" class="text-center text-sm text-gray-500">{{ message }}</div>
    </div>
  </div>
</template>
