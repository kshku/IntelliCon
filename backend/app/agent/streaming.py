from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph


@dataclass
class SSEEvent:
    event: str
    data: dict[str, Any] = field(default_factory=dict)

    def format(self) -> str:
        return f"data: {json.dumps(self.data)}\n\n"


async def stream_agent_response(
    graph: StateGraph,
    initial_state: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> AsyncGenerator[SSEEvent, None]:
    compiled = graph.compile()
    try:
        async for event in compiled.astream_events(initial_state, config or {}, version="v2"):
            kind = event.get("event", "")
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if isinstance(chunk, AIMessage) and chunk.content:
                    yield SSEEvent(
                        event="message",
                        data={"content": chunk.content},
                    )
            elif kind == "on_tool_start":
                yield SSEEvent(
                    event="tool_call",
                    data={
                        "tool": event.get("name", ""),
                        "args": event.get("data", {}).get("input", {}),
                    },
                )
            elif kind == "on_tool_end":
                yield SSEEvent(
                    event="tool_result",
                    data={
                        "tool": event.get("name", ""),
                        "output": str(event.get("data", {}).get("output", "")),
                    },
                )
        yield SSEEvent(event="done", data={})
    except Exception as exc:
        yield SSEEvent(event="error", data={"error": str(exc)})
