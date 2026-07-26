from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.agent.state import AgentState

logger = logging.getLogger(__name__)

MESSAGE_TYPES = {
    "human": HumanMessage,
    "ai": AIMessage,
    "system": SystemMessage,
    "tool": ToolMessage,
}

SESSION_TTL_SECONDS = 86400  # 24 hours


def _serialize_messages(messages: list) -> list[dict[str, Any]]:
    serialized = []
    for msg in messages:
        entry: dict[str, Any] = {
            "type": msg.type,
            "content": msg.content,
        }
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            entry["tool_calls"] = msg.tool_calls
        if hasattr(msg, "name") and msg.name:
            entry["name"] = msg.name
        if hasattr(msg, "tool_call_id") and msg.tool_call_id:
            entry["tool_call_id"] = msg.tool_call_id
        serialized.append(entry)
    return serialized


def _deserialize_messages(data: list[dict[str, Any]]) -> list:
    messages = []
    for entry in data:
        msg_type = entry.get("type", "human")
        msg_cls = MESSAGE_TYPES.get(msg_type, HumanMessage)
        kwargs: dict[str, Any] = {"content": entry.get("content", "")}
        if "tool_calls" in entry and entry["tool_calls"]:
            kwargs["tool_calls"] = entry["tool_calls"]
        if "name" in entry and entry["name"]:
            kwargs["name"] = entry["name"]
        if "tool_call_id" in entry and entry["tool_call_id"]:
            kwargs["tool_call_id"] = entry["tool_call_id"]
        messages.append(msg_cls(**kwargs))
    return messages


class SessionManager:
    _fallback_store: dict[str, str] = {}

    def __init__(self, redis_url: str) -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def save_session(self, session_id: str, state: AgentState) -> None:
        data = {
            "messages": _serialize_messages(state["messages"]),
            "session_id": state["session_id"],
            "context": state.get("context", {}),
            "iteration_count": state.get("iteration_count", 0),
        }
        key = f"session:{session_id}"
        serialized_data = json.dumps(data, default=str)
        try:
            await self._redis.setex(key, SESSION_TTL_SECONDS, serialized_data)
            logger.info("Session saved to Redis: %s", session_id)
        except Exception as e:
            logger.warning("Redis is not available, falling back to in-memory store. Error: %s", e)
            self._fallback_store[key] = serialized_data

    async def load_session(self, session_id: str) -> AgentState | None:
        key = f"session:{session_id}"
        raw = None
        try:
            raw = await self._redis.get(key)
        except Exception as e:
            logger.warning("Redis is not available, loading from in-memory store. Error: %s", e)
            raw = self._fallback_store.get(key)

        if raw is None:
            return None
        data = json.loads(raw)
        return {
            "messages": _deserialize_messages(data["messages"]),
            "session_id": data["session_id"],
            "context": data.get("context", {}),
            "iteration_count": data.get("iteration_count", 0),
        }

    async def delete_session(self, session_id: str) -> None:
        key = f"session:{session_id}"
        try:
            await self._redis.delete(key)
            logger.info("Session deleted from Redis: %s", session_id)
        except Exception as e:
            logger.warning("Redis is not available for deletion. Error: %s", e)
            self._fallback_store.pop(key, None)

    async def close(self) -> None:
        try:
            await self._redis.aclose()
        except Exception:
            pass
