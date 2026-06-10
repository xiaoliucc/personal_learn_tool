"""
AI 服务 — 支持 Anthropic Claude 和 DeepSeek

通过环境变量 AI_PROVIDER 切换：
- anthropic（默认）：使用 Claude API（claude-sonnet-4-6）
- deepseek：使用 DeepSeek API（deepseek-chat，OpenAI 兼容）

设置 API Key：
- Anthropic: export ANTHROPIC_API_KEY=xxx
- DeepSeek:  export AI_PROVIDER=deepseek
             export DEEPSEEK_API_KEY=xxx
"""

import json
from ..config import AI_PROVIDER, ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

# ---------------------------------------------------------------------------
# Prompt 模板（与具体 Provider 无关）
# ---------------------------------------------------------------------------

CLASSIFY_SYSTEM = """你是一个知识分类专家。请为以下学习资料推荐合适的标签。

要求：
1. 分析内容的主题和领域，推荐 2-5 个标签
2. 每个标签附带 0.0~1.0 的置信度
3. 为每个标签建议一个合适的颜色（十六进制）
4. 优先使用通用、可复用的标签名（如"Python"而非"Python装饰器详解"）

请严格返回 JSON 格式，不要包含其他文字：
{
  "tags": [
    {"name": "标签名", "confidence": 0.95, "color": "#3b82f6"}
  ]
}"""

SUMMARIZE_SYSTEM = """你是一个学习助手。请为以下资料生成精炼的摘要和关键要点。

要求：
1. 摘要简洁全面，覆盖核心内容，200 字以内
2. 关键要点 3-5 条，每条一句话
3. 用中文回答

请严格返回 JSON 格式：
{
  "summary": "摘要内容...",
  "key_points": ["要点1", "要点2", "要点3"]
}"""

# 当前使用的模型名（根据 Provider 不同）
if AI_PROVIDER == "deepseek":
    DEFAULT_MODEL = DEEPSEEK_MODEL
else:
    DEFAULT_MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Provider: Anthropic Claude
# ---------------------------------------------------------------------------

class _AnthropicProvider:
    """Anthropic Claude API 调用"""

    def __init__(self):
        from anthropic import AsyncAnthropic
        self._client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def chat(self, system: str, user_text: str, max_tokens: int = 800) -> dict:
        response = await self._client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_text}],
        )
        text = response.content[0].text
        return _parse_json(text)


# ---------------------------------------------------------------------------
# Provider: DeepSeek (OpenAI 兼容)
# ---------------------------------------------------------------------------

class _DeepSeekProvider:
    """DeepSeek API 调用（通过 OpenAI SDK）"""

    def __init__(self):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )

    async def chat(self, system: str, user_text: str, max_tokens: int = 800) -> dict:
        response = await self._client.chat.completions.create(
            model=DEFAULT_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
        )
        text = response.choices[0].message.content or ""
        return _parse_json(text)


# ---------------------------------------------------------------------------
# Provider 选择
# ---------------------------------------------------------------------------

if AI_PROVIDER == "deepseek":
    _provider = _DeepSeekProvider()
else:
    _provider = _AnthropicProvider()


# ---------------------------------------------------------------------------
# 对外接口
# ---------------------------------------------------------------------------

async def classify_material(title: str, content: str | None) -> dict:
    """
    对资料进行自动分类和标签建议。
    返回: {"tags": [{"name": str, "confidence": float, "color": str}]}
    """
    user_text = f"标题：{title}\n\n"
    user_text += f"内容：\n{content[:3000]}" if content else "（无正文内容）"
    return await _provider.chat(CLASSIFY_SYSTEM, user_text, max_tokens=500)


async def summarize_material(title: str, content: str | None) -> dict:
    """
    生成资料摘要和关键要点。
    返回: {"summary": str, "key_points": [str]}
    """
    user_text = f"标题：{title}\n\n"
    user_text += f"内容：\n{content[:5000]}" if content else "（无正文内容）"
    return await _provider.chat(SUMMARIZE_SYSTEM, user_text, max_tokens=800)


CONNECT_SYSTEM = """你是一个知识图谱专家。给定一篇新资料和一组已有资料的列表，请找出新资料与已有资料之间的语义关联。

关联类型：
- prerequisite: A 是 B 的前置知识
- extends: B 是 A 的延伸或深入
- related: 两者内容相关
- contradicts: 两者观点矛盾

请严格返回 JSON 数组，每个关联一个对象。只返回有明确关联的（strength > 0.5），最多 5 条：
[
  {"material_id": "已有资料ID", "relation_type": "related", "description": "关联说明", "strength": 0.8}
]

如果没有明显关联，返回空数组 []。"""


async def find_connections(
    title: str,
    content: str | None,
    existing_materials: list[dict],
) -> list[dict]:
    """
    发现新资料与已有资料的关联。

    参数:
    - existing_materials: [{"id": str, "title": str, "summary": str | None}]

    返回: [{"material_id": str, "relation_type": str, "description": str, "strength": float}]
    """
    if not existing_materials:
        return []

    # 构建已有资料列表文本
    existing_text = ""
    for i, m in enumerate(existing_materials[:20]):  # 最多 20 条，控制 token
        summary = m.get("summary", "") or ""
        existing_text += f"[{i}] ID={m['id']} 标题={m['title']}"
        if summary:
            existing_text += f" 摘要={summary[:100]}"
        existing_text += "\n"

    user_text = f"新资料：\n标题：{title}\n"
    if content:
        user_text += f"内容：{content[:2000]}\n\n"
    user_text += f"已有资料列表：\n{existing_text}"

    return await _provider.chat(CONNECT_SYSTEM, user_text, max_tokens=800)


async def process_material(
    title: str,
    content: str | None,
    progress_callback=None,
) -> dict:
    """
    对资料执行完整的 AI 处理流程（分类 + 摘要）。
    progress_callback(task_id, progress, message) 用于 WebSocket 推送。
    """
    result = {"tags": [], "summary": None, "key_points": []}

    # 步骤 1：分类
    if progress_callback:
        await progress_callback(0.1, "正在分析内容，推荐标签...")
    try:
        result["tags"] = (await classify_material(title, content))["tags"]
    except Exception as e:
        if progress_callback:
            await progress_callback(0.3, f"标签生成失败：{e}")

    # 步骤 2：摘要
    if progress_callback:
        await progress_callback(0.5, "正在生成摘要...")
    try:
        summary_data = await summarize_material(title, content)
        result["summary"] = summary_data["summary"]
        result["key_points"] = summary_data.get("key_points", [])
    except Exception as e:
        if progress_callback:
            await progress_callback(0.8, f"摘要生成失败：{e}")

    if progress_callback:
        await progress_callback(1.0, "处理完成")

    return result


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

def _parse_json(text: str) -> dict:
    """从 AI 返回的文本中提取 JSON。兼容 ```json ... ``` 包裹的情况。"""
    text = text.strip()
    if text.startswith("```"):
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
    return json.loads(text)
