from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import build_agent_graph
from app.agent.state import AgentState
from app.tools.base import ToolRegistry
from app.tools.sample import CalculatorTool


class TestAgentGraph:
    def test_graph_compiles(self) -> None:
        mock_llm = MagicMock()
        registry = ToolRegistry()
        registry.register(CalculatorTool())

        graph = build_agent_graph(mock_llm, registry, max_iterations=10)
        compiled = graph.compile()
        assert compiled is not None

    def test_graph_has_expected_nodes(self) -> None:
        mock_llm = MagicMock()
        registry = ToolRegistry()
        registry.register(CalculatorTool())

        graph = build_agent_graph(mock_llm, registry, max_iterations=10)
        assert "agent" in graph.nodes
        assert "tools" in graph.nodes

    async def test_agent_node_calls_llm(self) -> None:
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = AsyncMock()
        mock_llm.bind_tools.return_value.ainvoke.return_value = AIMessage(
            content="I'll calculate that for you."
        )

        registry = ToolRegistry()
        registry.register(CalculatorTool())

        from app.agent.graph import _agent_node

        agent_fn = _agent_node(mock_llm)
        state: AgentState = {
            "messages": [HumanMessage(content="What is 2+2?")],
            "session_id": "test",
            "context": {},
            "iteration_count": 0,
        }
        result = await agent_fn(state)
        assert "messages" in result
        assert result["iteration_count"] == 1
        mock_llm.bind_tools.assert_called_once()

    def test_should_continue_with_tool_calls(self) -> None:
        from app.agent.graph import _should_continue

        tool_call = {"id": "1", "name": "calc", "args": {}}
        state: AgentState = {
            "messages": [AIMessage(content="", tool_calls=[tool_call])],
            "session_id": "test",
            "context": {},
            "iteration_count": 1,
        }
        assert _should_continue(state, max_iterations=10) == "tools"

    def test_should_continue_without_tool_calls(self) -> None:
        from app.agent.graph import _should_continue

        state: AgentState = {
            "messages": [AIMessage(content="The answer is 4.")],
            "session_id": "test",
            "context": {},
            "iteration_count": 1,
        }
        assert _should_continue(state, max_iterations=10) == "__end__"

    def test_should_stop_at_max_iterations(self) -> None:
        from app.agent.graph import _should_continue

        tool_call = {"id": "1", "name": "calc", "args": {}}
        state: AgentState = {
            "messages": [AIMessage(content="", tool_calls=[tool_call])],
            "session_id": "test",
            "context": {},
            "iteration_count": 10,
        }
        assert _should_continue(state, max_iterations=10) == "__end__"
