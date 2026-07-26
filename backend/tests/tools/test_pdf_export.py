import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.tools.pdf_export import (
    PDF_OUTPUT_DIR,
    PdfExportTool,
    _cleanup_old_pdfs,
    _format_message_content,
)


@pytest.fixture
def tool():
    return PdfExportTool()


@pytest.fixture
def sample_messages():
    return [
        HumanMessage(content="How many theft cases in Mangaluru?"),
        AIMessage(
            content="I'll query the database for you.",
            tool_calls=[{"name": "sql_query", "args": {"question": "theft cases"}, "id": "tc1"}],
        ),
        ToolMessage(
            content="Found 42 cases matching the criteria.",
            tool_call_id="tc1",
        ),
        AIMessage(content="There are 42 theft cases registered in Mangaluru."),
    ]


def test_tool_metadata(tool):
    assert tool.name == "pdf_export"
    assert "session_id" in tool.input_schema["properties"]
    assert "title" in tool.input_schema["properties"]
    assert tool.input_schema["required"] == ["session_id"]


def test_format_message_content_string():
    assert _format_message_content("hello") == "hello"


def test_format_message_content_list():
    content = [{"text": "part1"}, {"text": "part2"}]
    result = _format_message_content(content)
    assert "part1" in result
    assert "part2" in result


def test_format_message_content_none():
    assert _format_message_content(None) == ""


def test_format_message_content_int():
    assert _format_message_content(42) == "42"


def test_missing_session_id(tool):
    result = asyncio.get_event_loop().run_until_complete(tool.execute())
    assert not result.success
    assert "session_id is required" in result.error


def test_empty_session_id(tool):
    result = asyncio.get_event_loop().run_until_complete(tool.execute(session_id=""))
    assert not result.success
    assert "session_id is required" in result.error


def test_session_not_found(tool):
    async def mock_load(sid):
        return None

    mock_manager = MagicMock()
    mock_manager.load_session = mock_load
    mock_manager.close = AsyncMock()

    with patch("app.agent.session.SessionManager", return_value=mock_manager):
        result = asyncio.get_event_loop().run_until_complete(tool.execute(session_id="nonexistent"))
    assert not result.success
    assert "not found or expired" in result.error


def test_session_empty_messages(tool):
    async def mock_load(sid):
        return {"messages": [], "session_id": sid, "context": {}, "iteration_count": 0}

    mock_manager = MagicMock()
    mock_manager.load_session = mock_load
    mock_manager.close = AsyncMock()

    with patch("app.agent.session.SessionManager", return_value=mock_manager):
        result = asyncio.get_event_loop().run_until_complete(
            tool.execute(session_id="empty-session")
        )
    assert not result.success
    assert "no messages" in result.error


def test_generate_pdf(tool, sample_messages):
    path = tool._generate_pdf(
        session_id="test-session",
        title="Test Report",
        messages=sample_messages,
        context={"user_id": "officer-1"},
    )
    assert os.path.exists(path)
    assert path.endswith(".pdf")
    assert os.path.getsize(path) > 0

    os.remove(path)


def test_generate_pdf_ai_with_tool_calls(tool):
    messages = [
        HumanMessage(content="Find repeat offenders"),
        AIMessage(
            content="Let me check the graph.",
            tool_calls=[
                {"name": "graph_query", "args": {"query_type": "degree_centrality"}, "id": "tc1"}
            ],
        ),
        ToolMessage(content="Found 5 repeat offenders.", tool_call_id="tc1"),
    ]
    path = tool._generate_pdf(
        session_id="tc-session",
        title="Tool Call Report",
        messages=messages,
        context={},
    )
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    os.remove(path)


def test_generate_pdf_special_characters(tool):
    messages = [
        HumanMessage(content="Show cases with <script>alert('xss')</script>"),
        AIMessage(content="Here are cases & their details."),
    ]
    path = tool._generate_pdf(
        session_id="xss-session",
        title="XSS Test",
        messages=messages,
        context={},
    )
    assert os.path.exists(path)
    os.remove(path)


def test_generate_pdf_default_title(tool):
    messages = [HumanMessage(content="Hello")]
    path = tool._generate_pdf(
        session_id="default-title",
        title="Investigation Report",
        messages=messages,
        context={},
    )
    assert os.path.exists(path)
    os.remove(path)


def test_cleanup_old_pdfs(tool):
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    test_file = os.path.join(PDF_OUTPUT_DIR, "test_old_file.pdf")
    with open(test_file, "w") as f:
        f.write("test")

    os.utime(test_file, (0, 0))

    _cleanup_old_pdfs()
    assert not os.path.exists(test_file)


def test_cleanup_keeps_recent_pdfs(tool):
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    test_file = os.path.join(PDF_OUTPUT_DIR, "test_recent_file.pdf")
    with open(test_file, "w") as f:
        f.write("test")

    _cleanup_old_pdfs()
    assert os.path.exists(test_file)
    os.remove(test_file)


def test_execute_full_flow(tool, sample_messages):
    async def mock_load(sid):
        return {
            "messages": sample_messages,
            "session_id": sid,
            "context": {"user_id": "officer-1"},
            "iteration_count": 3,
        }

    mock_manager = MagicMock()
    mock_manager.load_session = mock_load
    mock_manager.close = AsyncMock()

    with patch("app.agent.session.SessionManager", return_value=mock_manager):
        result = asyncio.get_event_loop().run_until_complete(
            tool.execute(session_id="full-flow", title="Test Report")
        )

    assert result.success
    assert "PDF exported successfully" in result.data
    assert result.metadata["message_count"] == 4
    assert result.metadata["session_id"] == "full-flow"
    assert result.metadata["download_url"].startswith("/api/pdf/")

    if os.path.exists(result.metadata["pdf_path"]):
        os.remove(result.metadata["pdf_path"])
