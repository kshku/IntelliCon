from collections.abc import Callable, Sequence
from typing import Any, Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.state import AgentState
from app.tools.base import ToolRegistry


def _agent_node(llm: BaseChatModel, tools: Sequence[Any] | None = None) -> Callable:
    async def agent(state: AgentState) -> dict:
        from langchain_core.messages import SystemMessage
        from app.agent.system_prompt import get_system_prompt

        system_prompt = get_system_prompt()
        messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

        _tools = tools if tools is not None else state.get("tools", [])
        response = await llm.bind_tools(_tools).ainvoke(messages)  # type: ignore[arg-type]
        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    return agent


def _should_continue(state: AgentState, max_iterations: int) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        if state.get("iteration_count", 0) >= max_iterations:
            return END  # type: ignore[return-value]
        return "tools"
    return END  # type: ignore[return-value]


def build_agent_graph(
    llm: BaseChatModel,
    tool_registry: ToolRegistry,
    max_iterations: int = 10,
) -> StateGraph:
    tools = tool_registry.get_langchain_tools()
    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", _agent_node(llm, tools))
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")

    def continue_condition(state: AgentState) -> str:
        return _should_continue(state, max_iterations)

    graph.add_conditional_edges("agent", continue_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph
