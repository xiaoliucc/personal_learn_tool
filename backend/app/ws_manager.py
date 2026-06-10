"""
WebSocket 连接管理器

管理所有活跃的 WebSocket 连接，支持：
- 向特定客户端推送消息
- 广播消息到所有连接的客户端
- 自动清理断开的连接
"""

import json
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket 连接管理器（单例）"""

    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """移除断开连接"""
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict):
        """向单个客户端发送 JSON 消息"""
        try:
            await websocket.send_json(data)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, data: dict):
        """向所有连接的客户端广播消息"""
        disconnected = []
        for ws in self._connections:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    @property
    def active_count(self) -> int:
        return len(self._connections)


# 全局单例
ws_manager = ConnectionManager()
