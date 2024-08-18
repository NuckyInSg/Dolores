import os
from abc import ABC, abstractmethod
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
import re

class BaseAgent(ABC):
    def __init__(self, api_key, resume_content: str, job_description_content: str, model="claude-3-sonnet-20240229", api_url="https://api.anthropic.com"):
        self.api_key = api_key
        self.resume_content = resume_content
        self.job_description_content = job_description_content
        self.model = model
        self.api_url = api_url
        
        self.llm = ChatAnthropic(
            anthropic_api_url=self.api_url,
            model=self.model,
            temperature=0,
            api_key=self.api_key
        )
        
        self.interview_chain = self._create_interview_chain()

    @abstractmethod
    def get_prompt(self):
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

    @staticmethod
    def extract_interviewer_content(text):
        pattern = r'<interviewer>(.*?)</interviewer>'
        matches = re.findall(pattern, text, re.DOTALL)
        return '\n'.join(match.strip() for match in matches)

    @staticmethod
    def extract_interview_stage(text):
        pattern = r'<interview_stage>(.*?)</interview_stage>'
        matches = re.findall(pattern, text, re.DOTALL)
        return '\n'.join(match.strip() for match in matches)

    async def conduct_interview(self, session_id):
        config = {"configurable": {"session_id": session_id}}

        # Initialize the conversation
        response = await self.interview_chain.ainvoke(
            {
                "input": "Start the interview with the introduction and small talk stage."
            },
            config=config
        )
        stage = self.extract_interview_stage(response)
        interviewer_content = self.extract_interviewer_content(response)
        print(f"Stage: {stage}")
        print(f"Interviewer: {interviewer_content}")

        # Main interview loop
        while True:
            answer = input("Candidate: ")
            if answer.lower() == 'end interview':
                break

            response = await self.interview_chain.ainvoke(
                {
                    "input": f"The candidate's response: {answer}\nContinue the interview based on the current stage and the candidate's response."
                },
                config=config
            )
            stage = self.extract_interview_stage(response)
            interviewer_content = self.extract_interviewer_content(response)
            print(f"Stage: {stage}")
            print(f"Interviewer: {interviewer_content}")

        # Closing remarks
        response = await self.interview_chain.ainvoke(
            {
                "input": "Provide closing remarks and explain the next steps in the hiring process."
            },
            config=config
        )
        stage = self.extract_interview_stage(response)
        interviewer_content = self.extract_interviewer_content(response)
        print(f"Stage: {stage}")
        print(f"Interviewer: {interviewer_content}")