// 学习收集工具 — 浏览器扩展 popup

const API_BASE = 'http://localhost:8000/api';

// ---- 获取当前标签页信息 ----
async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  document.getElementById('title').value = tab.title || '';
  document.getElementById('urlDisplay').textContent = tab.url || '';

  // 恢复上次输入的标签
  const { lastTags } = await chrome.storage.local.get('lastTags');
  if (lastTags) document.getElementById('tags').value = lastTags;
}

// ---- 保存 ----
document.getElementById('saveBtn').addEventListener('click', async () => {
  const btn = document.getElementById('saveBtn');
  const status = document.getElementById('status');
  const title = document.getElementById('title').value.trim();
  const tags = document.getElementById('tags').value.trim();
  const note = document.getElementById('note').value.trim();
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!title) {
    status.textContent = '请输入标题';
    status.className = 'status error';
    return;
  }

  btn.disabled = true;
  btn.textContent = '保存中...';
  status.textContent = '';
  status.className = 'status';

  try {
    // 创建 link 类型资料
    const res = await fetch(`${API_BASE}/materials`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'link',
        title: title,
        url: tab.url,
        content: note || undefined,
        source: tags || undefined,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || '保存失败');
    }

    // 记住标签
    if (tags) await chrome.storage.local.set({ lastTags: tags });

    status.textContent = '✅ 已保存！';
    status.className = 'status success';

    // 1.5 秒后关闭弹窗
    setTimeout(() => window.close(), 1500);
  } catch (e) {
    status.textContent = `❌ ${e.message}`;
    status.className = 'status error';
  } finally {
    btn.disabled = false;
    btn.textContent = '💾 保存';
  }
});

// ---- 键盘快捷键 ----
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    document.getElementById('saveBtn').click();
  }
});

// 启动
init();
