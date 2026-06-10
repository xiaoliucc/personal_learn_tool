# LearnVault — 个人学习资料收集工具

基于 AI 的个人学习资料收集、整理和复习工具。支持笔记、网页链接、代码片段三种资料类型，通过 AI 自动分类、摘要、知识关联和间隔重复复习。

## 功能

- 📚 **多类型资料**：笔记（Markdown）、网页链接、代码片段
- 🤖 **AI 智能处理**：自动分类打标签 + 生成摘要 + 发现知识关联
- 🔗 **知识图谱**：可视化资料间的关联网络
- 📝 **SM-2 间隔重复**：基于遗忘曲线的智能复习调度
- 🌙 **暗色模式**：支持浅色/暗色切换
- 📱 **PWA 离线**：可安装到桌面，离线访问已有资料
- 🧩 **浏览器扩展**：一键保存网页链接

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python FastAPI + SQLAlchemy + SQLite |
| 前端 | Vue 3 + TypeScript + Vite + Tailwind CSS |
| AI | Anthropic Claude / DeepSeek（可切换） |
| 图谱 | vis-network |
| 编辑器 | markdown-it（GFM） |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/xiaoliucc/personal_learn_tool.git
cd personal_learn_tool
```

### 2. 后端

```bash
cd backend

# 安装 uv（如果还没有）
pip install uv

# 同步依赖（自动创建虚拟环境）
uv sync

# 配置 AI（创建 ~/.learning-collector/.env）
mkdir -p ~/.learning-collector
cat > ~/.learning-collector/.env << EOF
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的API密钥
DEEPSEEK_MODEL=deepseek-chat
EOF

# 启动
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`

### 4. 浏览器扩展（可选）

1. Edge 打开 `edge://extensions/`
2. 开启"开发人员模式"
3. 加载 `browser-extension/` 文件夹

## AI Provider 配置

支持两种 AI 后端，通过 `~/.learning-collector/.env` 中的 `AI_PROVIDER` 切换：

| Provider | 环境变量 | 模型 |
|---|---|---|
| DeepSeek | `AI_PROVIDER=deepseek` `DEEPSEEK_API_KEY=sk-xxx` | `deepseek-chat` |
| Anthropic | `AI_PROVIDER=anthropic` `ANTHROPIC_API_KEY=sk-xxx` | `claude-sonnet-4-6` |

## 数据存储

用户数据默认存储在 `~/.learning-collector/data.db`，可通过环境变量修改：

```bash
export LEARNING_DATA_DIR=/your/custom/path
```

## 项目结构

```
├── backend/               # Python FastAPI
│   ├── app/
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── routes/        # API 路由
│   │   ├── services/      # AI + 复习服务
│   │   └── schemas/       # Pydantic 校验
│   └── pyproject.toml     # uv 依赖管理
├── frontend/              # Vue 3 + Vite
│   └── src/
│       ├── components/    # 组件
│       ├── pages/         # 页面
│       ├── stores/        # Pinia 状态
│       ├── api/           # API 调用
│       ├── composables/   # 组合式函数
│       └── router/        # 路由
├── browser-extension/     # Chrome/Edge 扩展
└── 实现计划.md            # 完整设计文档
```

## 关键依赖版本

| 包 | 版本 | 备注 |
|---|---|---|
| vue-router | **4.5.1** | 5.x 与 Edge 有兼容问题 |
| tailwindcss | 4.x | @tailwindcss/vite |
| vis-network | latest | 知识图谱 |

## License

MIT
