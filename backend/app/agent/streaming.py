from __future__ import annotations

import json
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph.state import CompiledStateGraph


@dataclass
class SSEEvent:
    event: str
    data: dict[str, Any] = field(default_factory=dict)

    def format(self) -> str:
        return f"data: {json.dumps(self.data)}\n\n"


async def stream_agent_response(
    graph: CompiledStateGraph,
    initial_state: dict[str, Any],
    config: dict[str, Any] | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> AsyncGenerator[SSEEvent, None]:
    from app.audit import log_audit_step

    step_counter = 0
    step_start: float | None = None

    # Buffers for active chat model runs to separate intermediate thinking from final answer
    run_buffers: dict[str, list[str]] = {}

    try:
        async for event in graph.astream_events(initial_state, config or {}, version="v2"):  # type: ignore[arg-type,call-overload]
            kind = event.get("event", "")
            if kind == "on_chat_model_start":
                run_id = event.get("run_id")
                if run_id:
                    run_buffers[run_id] = []
            elif kind == "on_chat_model_stream":
                run_id = event.get("run_id")
                chunk = event.get("data", {}).get("chunk")
                if isinstance(chunk, AIMessage) and chunk.content:
                    content = chunk.content
                    if isinstance(content, str) and run_id:
                        run_buffers.setdefault(run_id, []).append(content)
            elif kind == "on_chat_model_end":
                run_id = event.get("run_id")
                output = event.get("data", {}).get("output")
                if isinstance(output, AIMessage) and run_id:
                    has_tool_calls = bool(output.tool_calls)
                    buffered_text = "".join(run_buffers.get(run_id, []))
                    
                    if has_tool_calls:
                        if buffered_text:
                            step_counter += 1
                            await log_audit_step(
                                session_id=session_id,
                                user_id=user_id,
                                step_number=step_counter,
                                step_type="reasoning",
                                content=buffered_text,
                            )
                            yield SSEEvent(event="reasoning", data={"content": buffered_text})
                    else:
                        if buffered_text:
                            yield SSEEvent(event="message", data={"content": buffered_text})
                    
                    run_buffers.pop(run_id, None)
            elif kind == "on_tool_start":
                step_start = time.monotonic()
                tool_name = event.get("name", "")
                tool_input = event.get("data", {}).get("input", {})
                yield SSEEvent(
                    event="tool_call",
                    data={"tool": tool_name, "args": tool_input},
                )
            elif kind == "on_tool_end":
                tool_name = event.get("name", "")
                tool_output = str(event.get("data", {}).get("output", ""))
                duration_ms = int((time.monotonic() - step_start) * 1000) if step_start else None
                yield SSEEvent(
                    event="tool_result",
                    data={"tool": tool_name, "output": tool_output},
                )
                step_counter += 1
                sql_executed = None
                try:
                    parsed = json.loads(tool_output)
                    if isinstance(parsed, dict) and "metadata" in parsed:
                        sql_executed = parsed["metadata"].get("sql")
                except (json.JSONDecodeError, TypeError):
                    pass
                await log_audit_step(
                    session_id=session_id,
                    user_id=user_id,
                    step_number=step_counter,
                    step_type="tool_call",
                    content=tool_name,
                    tool_output=tool_output,
                    sql_executed=sql_executed,
                    duration_ms=duration_ms,
                )
                step_start = None
        yield SSEEvent(event="done", data={})
    except Exception as exc:
        yield SSEEvent(event="error", data={"error": str(exc)})
