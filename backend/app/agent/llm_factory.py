from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from app.config import settings


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> BaseChatModel:
    provider = (provider or settings.LLM_PROVIDER).lower()
    api_key = api_key or settings.LLM_API_KEY or "mock-key"
    model = model or settings.LLM_MODEL

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, api_key=api_key)  # type: ignore[arg-type]
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model, api_key=api_key)  # type: ignore[arg-type, call-arg]
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)  # type: ignore[call-arg]

    raise ValueError(f"Unknown LLM provider: {provider!r}. Supported: openai, anthropic, gemini")
