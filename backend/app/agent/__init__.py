from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

from app.agent.graph import build_agent_graph
from app.agent.llm_factory import get_llm
from app.agent.session import SessionManager
from app.agent.state import AgentState
from app.agent.streaming import SSEEvent, stream_agent_response
from app.agent.system_prompt import get_system_prompt
from app.config import settings
from app.tools.base import ToolRegistry
from app.tools.registry import tool_registry

__all__ = [
    "AgentState",
    "SSEEvent",
    "SessionManager",
    "create_agent",
    "get_llm",
    "get_system_prompt",
    "stream_agent_response",
    "tool_registry",
]


def create_agent(
    llm: BaseChatModel | None = None,
    registry: ToolRegistry | None = None,
    max_iterations: int | None = None,
) -> tuple[CompiledStateGraph, SessionManager]:
    _llm = llm or get_llm()
    _registry = registry or tool_registry
    _max_iter = max_iterations or settings.AGENT_MAX_ITERATIONS

    graph = build_agent_graph(_llm, _registry, max_iterations=_max_iter)
    compiled_graph = graph.compile()
    session_manager = SessionManager(settings.REDIS_URL)
    return compiled_graph, session_manager
