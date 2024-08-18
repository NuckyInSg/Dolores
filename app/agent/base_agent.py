from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
import re

class BaseAgent(ABC):
    def __init__(self, llm: BaseChatModel, resume_content: str, job_description_content: str):
        self.llm = llm
        self.resume_content = resume_content
        self.job_description_content = job_description_content
        
        self.interview_chain = self._create_interview_chain()

        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0

    @abstractmethod
    def get_prompt(self):
        pass

    @abstractmethod
    def start_interview(self):
        pass

    @abstractmethod
    async def conduct_interview(self, session_id: str, user_input: str = None) -> dict:
        pass

    @abstractmethod
    def num_tokens_from_string(self, string: str) -> int:
        pass

    def _create_interview_chain(self):
        system_template = self.get_prompt()
        
        human_template = "{input}"

        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", human_template)
        ])

        chain = chat_prompt | self.llm | StrOutputParser()

        store = {}

        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in store:
                store[session_id] = InMemoryChatMessageHistory()
            return store[session_id]

        return RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def update_token_usage(self, prompt_tokens, completion_tokens):
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        # Calculate cost based on the model's pricing
        # This is a placeholder calculation, adjust according to actual pricing
        self.total_cost += (prompt_tokens * 0.00001 + completion_tokens * 0.00003)

    def get_token_usage(self):
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost": f"${self.total_cost:.4f}"
        }

    async def _call_llm(self, session_id: str, input_text: str) -> dict:
        config = {"configurable": {"session_id": session_id}}

        response = await self.interview_chain.ainvoke(
            {"input": input_text},
            config=config
        )

        stage = self.extract_interview_stage(response)
        interviewer_content = self.extract_interviewer_content(response)

        # Update token usage
        prompt_tokens = self.num_tokens_from_string(input_text)
        completion_tokens = self.num_tokens_from_string(response)
        self.update_token_usage(prompt_tokens, completion_tokens)

        return {
            "stage": stage,
            "interviewer_content": interviewer_content,
            "token_usage": self.get_token_usage()
        }