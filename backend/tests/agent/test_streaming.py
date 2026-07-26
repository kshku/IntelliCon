from __future__ import annotations

import json
from unittest.mock import MagicMock

from app.agent.streaming import SSEEvent, stream_agent_response


class TestSSEEvent:
    def test_format_message(self) -> None:
        event = SSEEvent(event="message", data={"content": "hello"})
        formatted = event.format()
        assert formatted.startswith("data: ")
        assert formatted.endswith("\n\n")
        parsed = json.loads(formatted.removeprefix("data: ").removesuffix("\n\n"))
        assert parsed["content"] == "hello"

    def test_format_done(self) -> None:
        event = SSEEvent(event="done", data={})
        formatted = event.format()
        parsed = json.loads(formatted.removeprefix("data: ").removesuffix("\n\n"))
        assert parsed == {}

    def test_format_error(self) -> None:
        event = SSEEvent(event="error", data={"error": "something failed"})
        parsed = json.loads(event.format().removeprefix("data: ").removesuffix("\n\n"))
        assert parsed["error"] == "something failed"


class TestStreamAgentResponse:
    async def test_yields_done_event(self) -> None:
        mock_graph = MagicMock()

        async def empty_stream(*args, **kwargs):
            return
            yield  # noqa: B029

        mock_graph.astream_events = empty_stream

        events = []
        async for event in stream_agent_response(mock_graph, {"messages": []}):
            events.append(event)

        assert len(events) == 1
        assert events[0].event == "done"

    async def test_yields_error_on_exception(self) -> None:
        mock_graph = MagicMock()

        async def failing_stream(*args, **kwargs):
            raise RuntimeError("test error")
            yield  # noqa: B029

        mock_graph.astream_events = failing_stream

        events = []
        async for event in stream_agent_response(mock_graph, {"messages": []}):
            events.append(event)

        assert len(events) == 1
        assert events[0].event == "error"
        assert "test error" in events[0].data["error"]
