"""LLM 调用薄封装:强制 tool use 拿结构化输出 + Pydantic 校验重试。

用 tool use 而非 output_config/messages.parse 的原因:兼容 Anthropic 协议的
第三方端点(如小米 MIMO)普遍支持 tool call,但不强制执行 json_schema;
tool use 在官方 API 上同样可靠,一条代码路径通吃。
"""
from typing import TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

from .. import config

T = TypeVar("T", bound=BaseModel)

_client: anthropic.Anthropic | None = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(
            api_key=config.ANTHROPIC_API_KEY or None)  # base_url 走 ANTHROPIC_BASE_URL 环境变量
    return _client


def call_structured(*, model: str, system: list | str, content, schema: type[T],
                    tool_name: str, tool_description: str,
                    max_tokens: int = 4096) -> tuple[T, dict]:
    """强制模型调用一个'提交结果'工具,返回 (校验后的对象, 用量)。校验失败自动重试一次。"""
    tool = {
        "name": tool_name,
        "description": tool_description,
        "input_schema": schema.model_json_schema(),
    }
    messages = [{"role": "user", "content": content}]
    last_err: Exception | None = None
    for _ in range(2):
        response = client().messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool_name},
        )
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cache_read": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
        }
        tool_use = next((b for b in response.content if b.type == "tool_use"), None)
        if tool_use is None:
            last_err = ValueError("模型未返回 tool_use 块")
            continue
        try:
            return schema.model_validate(tool_use.input), usage
        except ValidationError as e:
            last_err = e
            # 把校验错误喂回去重试一次
            messages = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": tool_use.id,
                     "content": f"参数校验失败,请重新调用 {tool_name}: {e}",
                     "is_error": True}]},
            ]
    raise last_err  # type: ignore[misc]
