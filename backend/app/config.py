import os
from pathlib import Path
from dotenv import load_dotenv

# 数据目录：默认 ~/.learning-collector/，可通过环境变量覆盖
DATA_DIR = Path(os.getenv("LEARNING_DATA_DIR", Path.home() / ".learning-collector"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 加载 .env 文件（数据目录下的 .env 优先级最高，其次项目根目录）
load_dotenv(DATA_DIR / ".env")   # 用户数据目录
load_dotenv(override=False)      # 项目根目录 .env（不覆盖已有值）

DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'data.db'}"

# ---- AI Provider 配置 ----
# 支持 "anthropic"（Claude）和 "deepseek"（DeepSeek）
# 在 .env 文件中设置，或通过系统环境变量设置
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").lower()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# DeepSeek（与 OpenAI 兼容的 API）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")