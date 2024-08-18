from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

def create_llm(
    name: str,
    version: str,
    api_key: str,
    api_url: Optional[str] = None,
    temperature: float = 0
) -> BaseChatModel:
    if name.lower() == "anthropic":
        return create_anthropic_llm(api_key, version, api_url, temperature)
    elif name.lower() == "openai":
        return create_openai_llm(api_key, version, api_url, temperature)
    else:
        raise ValueError(f"Unsupported LLM: {name}")

def create_anthropic_llm(
    api_key: str,
    model: str = "claude-3-sonnet-20240229",
    api_url: Optional[str] = None,
    temperature: float = 0
) -> BaseChatModel:
    return ChatAnthropic(
        anthropic_api_key=api_key,
        model=model,
        anthropic_api_url=api_url or "https://api.anthropic.com",
        temperature=temperature
    )

def create_openai_llm(
    api_key: str,
    model: str = "gpt-4",
    api_url: Optional[str] = None,
    temperature: float = 0
) -> BaseChatModel:
    return ChatOpenAI(
        openai_api_key=api_key,
        model=model,
        openai_api_base=api_url,
        temperature=temperature
    )