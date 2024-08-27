from abc import ABC, abstractmethod
from app.llm.chat_llm import ChatLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, llm: ChatLLM, resume_content: str, job_description_content: str):
        self.llm = llm
        self.resume_content = resume_content
        self.job_description_content = job_description_content
        
        self.interview_chain = self._create_interview_chain()


    @abstractmethod
    def get_prompt(self) -> str:
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
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


    def get_token_usage(self):
        return self.llm.get_token_usage()

    async def process_message(self, session_id: str, input: str) -> dict:
        config = {"configurable": {"session_id": session_id}}

        output = await self.interview_chain.ainvoke(
            {"input": input},
            config=config
        )

        parsed_response = self.parse_response(output)

        self.llm.update_token_usage(input, output)

        return parsed_response