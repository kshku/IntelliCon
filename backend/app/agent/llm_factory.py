from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from app.config import settings
import contextvars

# Context variables for active LLM overrides in the current async execution context
active_llm_provider: contextvars.ContextVar[str | None] = contextvars.ContextVar("active_llm_provider", default=None)
active_llm_model: contextvars.ContextVar[str | None] = contextvars.ContextVar("active_llm_model", default=None)
active_llm_api_key: contextvars.ContextVar[str | None] = contextvars.ContextVar("active_llm_api_key", default=None)


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> BaseChatModel:
    provider = (provider or active_llm_provider.get() or settings.LLM_PROVIDER).lower().strip()
    api_key = api_key or active_llm_api_key.get() or settings.LLM_API_KEY or "mock-key"
    if isinstance(api_key, str):
        api_key = api_key.strip()
    model = (model or active_llm_model.get() or settings.LLM_MODEL).strip()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, api_key=api_key)  # type: ignore[arg-type]
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model, api_key=api_key)  # type: ignore[arg-type, call-arg]
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)  # type: ignore[call-arg]
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=model, api_key=api_key)  # type: ignore[arg-type, call-arg]

    raise ValueError(f"Unknown LLM provider: {provider!r}. Supported: openai, anthropic, gemini, groq")
