# File: tests/mocks/mock_llm.py

from typing import Any, List, Optional, Dict
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import Runnable

class MockLLM(Runnable):
    responses: List[str]
    response_index: int
    model_name: str

    def __init__(self, responses: List[str], model_name: str = "mock-model"):
        self.responses = responses
        self.response_index = 0
        self.model_name = model_name

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> ChatResult:
        if self.response_index >= len(self.responses):
            raise IndexError("No more predefined responses available in MockLLM")
        
        response = self.responses[self.response_index]
        self.response_index += 1
        
        message = AIMessage(content=response)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def invoke(self, input: Dict[str, Any]) -> Any:
        messages = input.get("messages", [])
        result = self._generate(messages)
        return result.generations[0].message.content

    async def ainvoke(self, input: Dict[str, Any]) -> Any:
        return self.invoke(input)

    @property
    def _llm_type(self) -> str:
        return "mock"

def create_mock_llm(responses: List[str], model_name: str = "mock-model") -> MockLLM:
    return MockLLM(responses, model_name)