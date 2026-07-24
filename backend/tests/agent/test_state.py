from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.state import AgentState


class TestAgentState:
    def test_create_state(self) -> None:
        state: AgentState = {
            "messages": [HumanMessage(content="hello")],
            "session_id": "test-session",
            "context": {},
            "iteration_count": 0,
        }
        assert state["session_id"] == "test-session"
        assert len(state["messages"]) == 1
        assert state["iteration_count"] == 0

    def test_state_with_multiple_messages(self) -> None:
        messages = [
            HumanMessage(content="hello"),
            AIMessage(content="hi there"),
            HumanMessage(content="what tables are there?"),
        ]
        state: AgentState = {
            "messages": messages,
            "session_id": "sess-123",
            "context": {"database": "test_db"},
            "iteration_count": 3,
        }
        assert len(state["messages"]) == 3
        assert state["context"]["database"] == "test_db"

    def test_state_default_context(self) -> None:
        state: AgentState = {
            "messages": [],
            "session_id": "sess-456",
            "context": {},
            "iteration_count": 0,
        }
        assert state["context"] == {}
