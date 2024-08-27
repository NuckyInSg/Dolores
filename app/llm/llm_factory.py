from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from app.llm.chat_llm import ChatLLM
from typing import Dict

def create_llm(
        model: str,
        api_key: str,
        api_url: str,
        provider: str,
        extra_info: dict,
) -> ChatLLM:
    if provider.startswith("anthropic"):
        base_llm = create_anthropic_llm(model, api_key, api_url, 0)
    elif provider.startswith("openai"):
        base_llm = create_openai_llm(model, api_key, api_url, 0)
    
    return ChatLLM(
        model=base_llm,
        cost_million_input_token=extra_info["cost_input"],
        cost_million_output_token=extra_info["cost_output"],
        max_output_token=extra_info["max_output_token"],
        context_window=extra_info["context_window"],
        encoder=extra_info["encoder"]
    )
    

def create_anthropic_llm(
    model: str,
    api_key: str,
    api_url: Optional[str] = None,
    temperature: float = 0.3
) -> BaseChatModel:
    return ChatAnthropic(
        anthropic_api_key=api_key,
        model=model,
        anthropic_api_url=api_url,
        max_tokens=2048,
        temperature=temperature,
    )

def create_openai_llm(
    model: str,
    api_key: str,
    api_url: Optional[str] = None,
    temperature: float = 0.3
) -> BaseChatModel:
    return ChatOpenAI(
        openai_api_key=api_key,
        model=model,
        openai_api_base=api_url,
        temperature=temperature
    )