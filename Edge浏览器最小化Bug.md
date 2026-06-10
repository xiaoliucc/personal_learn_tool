# Edge 浏览器最小化按钮失效 Bug

> 发现：2026-06-09 | 解决：2026-06-10
> 状态：✅ 已修复
> Edge 版本：Windows 11 Edge（Chromium）

---

## 现象

Edge 打开项目页面后，浏览器最小化按钮（`_`）无响应。关闭页面恢复正常。
所有页面均受影响，Chrome/Firefox 正常。

## 根因

**vue-router 5.x 的 history 实现与 Edge 存在回归性兼容问题。**
`createWebHashHistory()` 和 `createWebHistory()` 注册的 `hashchange` / `popstate` 事件监听器触发 Edge 窗口管理 bug，导致最小化按钮失效。

vue-router 5.x 的公开 issue 中有同类报告。

## 解决方案

降级到 **vue-router@4.5.1**，使用标准 `createWebHashHistory()`。

```bash
npm install vue-router@4.5.1
```

```typescript
// router/index.ts — 标准 Hash Router，无需任何 workaround
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [...]
})
```

## 排查过程

通过逐模块二分法定位：

| 步骤 | 测试 | 结果 |
|------|------|------|
| 1 | 纯 Vue (Hello World) | ✅ 正常 |
| 2 | Vue + Tailwind | ✅ 正常 |
| 3 | Vue + Tailwind + Pinia | ✅ 正常 |
| 4 | Vue + Tailwind + Router (createRouter) | ❌ 失败 |
| 5 | 仅 import vue-router (不调 createRouter) | ✅ 正常 |
| 6 | createWebHashHistory | ❌ 失败 |
| 7 | createWebHistory | ❌ 失败 |
| 8 | createMemoryHistory + 轮询 | ✅ 正常（但 router-link 不兼容） |
| 9 | vue-router@4.5.1 + createWebHashHistory | ✅ 正常 |

## 已排除的假设

- CSS `h-screen` / `min-h-screen` / `position:fixed` / `height:100%`
- WebSocket 无限重连
- vis-network 组件
- Vite HMR（生产模式也存在）
- Pinia
- 单个页面/组件
