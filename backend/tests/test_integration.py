from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.agent import create_agent, tool_registry
from app.tools.registry import register_default_tools
from app.tools.sample import CalculatorTool


class TestCreateAgent:
    def test_create_agent_returns_graph_and_session(self) -> None:
        mock_llm = MagicMock()
        with patch("app.agent.settings") as mock_settings:
            mock_settings.AGENT_MAX_ITERATIONS = 10
            mock_settings.REDIS_URL = "redis://localhost:6379"
            graph, session = create_agent(llm=mock_llm)
            assert graph is not None
            assert session is not None

    def test_create_agent_with_custom_registry(self) -> None:
        from app.tools.base import ToolRegistry

        mock_llm = MagicMock()
        registry = ToolRegistry()
        registry.register(CalculatorTool())

        with patch("app.agent.settings") as mock_settings:
            mock_settings.AGENT_MAX_ITERATIONS = 5
            mock_settings.REDIS_URL = "redis://localhost:6379"
            graph, session = create_agent(llm=mock_llm, registry=registry)
            assert graph is not None

    def test_default_registry_has_calculator(self) -> None:
        register_default_tools()
        tool = tool_registry.get("calculator")
        assert tool is not None
        assert isinstance(tool, CalculatorTool)
