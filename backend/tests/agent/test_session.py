from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.session import SessionManager, _deserialize_messages, _serialize_messages
from app.agent.state import AgentState


class TestMessageSerialization:
    def test_serialize_human_message(self) -> None:
        messages = [HumanMessage(content="hello")]
        result = _serialize_messages(messages)
        assert len(result) == 1
        assert result[0]["type"] == "human"
        assert result[0]["content"] == "hello"

    def test_serialize_ai_message_with_tool_calls(self) -> None:
        messages = [
            AIMessage(
                content="",
                tool_calls=[{"id": "1", "name": "calc", "args": {"expression": "2+2"}}],
            )
        ]
        result = _serialize_messages(messages)
        assert result[0]["type"] == "ai"
        assert len(result[0]["tool_calls"]) == 1

    def test_roundtrip_serialization(self) -> None:
        original = [
            HumanMessage(content="hello"),
            AIMessage(content="hi there"),
            HumanMessage(content="what is 2+2?"),
        ]
        serialized = _serialize_messages(original)
        deserialized = _deserialize_messages(serialized)
        assert len(deserialized) == 3
        assert deserialized[0].content == "hello"
        assert deserialized[1].content == "hi there"
        assert deserialized[2].content == "what is 2+2?"


class TestSessionManager:
    def _make_state(self) -> AgentState:
        return {
            "messages": [HumanMessage(content="hello"), AIMessage(content="hi")],
            "session_id": "test-session",
            "context": {"db": "test"},
            "iteration_count": 2,
        }

    async def test_save_and_load_session(self) -> None:
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        with patch("app.agent.session.aioredis.from_url", return_value=mock_redis):
            manager = SessionManager("redis://localhost:6379")
            state = self._make_state()
            await manager.save_session("test-session", state)

            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            assert call_args[0][0] == "session:test-session"
            assert call_args[0][1] == 86400  # TTL

            saved_data = json.loads(call_args[0][2])
            assert saved_data["session_id"] == "test-session"
            assert saved_data["iteration_count"] == 2

    async def test_load_session_returns_none_when_missing(self) -> None:
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        with patch("app.agent.session.aioredis.from_url", return_value=mock_redis):
            manager = SessionManager("redis://localhost:6379")
            result = await manager.load_session("nonexistent")
            assert result is None

    async def test_load_session_deserializes(self) -> None:
        state = self._make_state()
        from app.agent.session import _serialize_messages

        saved_data = {
            "messages": _serialize_messages(state["messages"]),
            "session_id": state["session_id"],
            "context": state["context"],
            "iteration_count": state["iteration_count"],
        }

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps(saved_data, default=str))

        with patch("app.agent.session.aioredis.from_url", return_value=mock_redis):
            manager = SessionManager("redis://localhost:6379")
            result = await manager.load_session("test-session")
            assert result is not None
            assert result["session_id"] == "test-session"
            assert result["iteration_count"] == 2
            assert len(result["messages"]) == 2

    async def test_delete_session(self) -> None:
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock()

        with patch("app.agent.session.aioredis.from_url", return_value=mock_redis):
            manager = SessionManager("redis://localhost:6379")
            await manager.delete_session("test-session")
            mock_redis.delete.assert_called_once_with("session:test-session")
