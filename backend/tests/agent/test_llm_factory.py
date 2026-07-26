from __future__ import annotations

from unittest.mock import patch

import pytest


class TestLLMFactory:
    def test_get_llm_openai(self) -> None:
        from app.agent.llm_factory import get_llm

        with patch("app.agent.llm_factory.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "openai"
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4o"
            llm = get_llm()
            assert llm.model_name == "gpt-4o"  # type: ignore[attr-defined]

    def test_get_llm_anthropic(self) -> None:
        from app.agent.llm_factory import get_llm

        with patch("app.agent.llm_factory.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "anthropic"
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "claude-3-opus"
            llm = get_llm()
            assert llm.model == "claude-3-opus"  # type: ignore[attr-defined]

    def test_get_llm_gemini(self) -> None:
        from app.agent.llm_factory import get_llm

        with patch("app.agent.llm_factory.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "gemini"
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gemini-pro"
            llm = get_llm()
            assert "gemini-pro" in llm.model  # type: ignore[attr-defined]

    def test_get_llm_groq(self) -> None:
        from app.agent.llm_factory import get_llm

        with patch("app.agent.llm_factory.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "groq"
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "llama-3.3-70b-versatile"
            llm = get_llm()
            assert llm.model_name == "llama-3.3-70b-versatile"  # type: ignore[attr-defined]

    def test_get_llm_unknown_provider(self) -> None:
        from app.agent.llm_factory import get_llm

        with patch("app.agent.llm_factory.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "unknown"
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "some-model"
            with pytest.raises(ValueError, match="Unknown LLM provider"):
                get_llm()
