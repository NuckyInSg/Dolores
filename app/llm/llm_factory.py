from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

def create_llm(
    name: str,
    api_key: str,
    api_url: Optional[str] = None,
    temperature: float = 0
) -> BaseChatModel:
    if name.startswith('anthropic'):
        return create_anthropic_llm(name, api_key, api_url, temperature)
    elif name.startswith('openai'):
        return create_openai_llm(name, api_key, api_url, temperature)
    else:
        raise ValueError(f"Unsupported LLM: {name}")

def create_anthropic_llm(
    model: str,
    api_key: str,
    api_url: Optional[str] = None,
    temperature: float = 0
) -> BaseChatModel:
    return ChatAnthropic(
        anthropic_api_key=api_key,
        model=model,
        anthropic_api_url=api_url,
        temperature=temperature
    )

def create_openai_llm(
    model: str,
    api_key: str,
    api_url: Optional[str] = None,
    temperature: float = 0
) -> BaseChatModel:
    return ChatOpenAI(
        openai_api_key=api_key,
        model=model,
        openai_api_base=api_url,
        temperature=temperature
    )