from __future__ import annotations

from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.state import AgentState
from app.tools.base import ToolRegistry


def _agent_node(llm: BaseChatModel) -> callable:
    async def agent(state: AgentState) -> dict:
        response = await llm.bind_tools(state.get("tools", [])).ainvoke(state["messages"])
        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    return agent


def _should_continue(state: AgentState, max_iterations: int) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        if state.get("iteration_count", 0) >= max_iterations:
            return END
        return "tools"
    return END


def build_agent_graph(
    llm: BaseChatModel,
    tool_registry: ToolRegistry,
    max_iterations: int = 10,
) -> StateGraph:
    tools = tool_registry.get_langchain_tools()
    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", _agent_node(llm))
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")

    def continue_condition(state: AgentState) -> str:
        return _should_continue(state, max_iterations)

    graph.add_conditional_edges("agent", continue_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph
