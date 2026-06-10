/**
 * WebSocket 连接 composable
 *
 * 自动连接 /ws/processing，接收 AI 任务进度消息，
 * 断线时自动重连。
 */

import { ref, onMounted, onUnmounted } from 'vue'

/** WebSocket 进度消息 */
export interface WSMessage {
  task_id: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  message: string
  material_id?: string
  error?: string
}

export function useWebSocket() {
  const connected = ref(false)
  const lastMessage = ref<WSMessage | null>(null)
  const messages = ref<WSMessage[]>([])

  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let intentionalClose = false  // 标记是否主动断开，防止被动重连

  function connect() {
    // 构建 WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/ai/ws/processing`

    intentionalClose = false
    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      connected.value = true
    }

    ws.onmessage = (event) => {
      try {
        const data: WSMessage = JSON.parse(event.data)
        lastMessage.value = data
        messages.value.push(data)
      } catch {
        // 忽略非 JSON 消息
      }
    }

    ws.onclose = () => {
      connected.value = false
      // 只有非主动断开时才自动重连
      if (!intentionalClose) {
        reconnectTimer = setTimeout(connect, 3000)
      }
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function disconnect() {
    intentionalClose = true  // 必须先设标志，防止 onclose 触发重连
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (ws) {
      ws.close()
      ws = null
    }
    connected.value = false
  }

  onMounted(connect)
  onUnmounted(disconnect)

  return { connected, lastMessage, messages }
}
