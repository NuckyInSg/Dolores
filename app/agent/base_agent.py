from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
import re
import tiktoken

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

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self.llm.model_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

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

        # Update token usage
        prompt_tokens = self.num_tokens_from_string("Start the interview with the introduction and small talk stage.")
        completion_tokens = self.num_tokens_from_string(response)
        self.update_token_usage(prompt_tokens, completion_tokens)

        # Main interview loop
        while True:
            answer = input("Candidate: ")
            if answer.lower() in ['end interview', 'quit', 'exit']:
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

            # Update token usage
            prompt_tokens = self.num_tokens_from_string(f"The candidate's response: {answer}\nContinue the interview based on the current stage and the candidate's response.")
            completion_tokens = self.num_tokens_from_string(response)
            self.update_token_usage(prompt_tokens, completion_tokens)

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

        # Update token usage
        prompt_tokens = self.num_tokens_from_string("Provide closing remarks and explain the next steps in the hiring process.")
        completion_tokens = self.num_tokens_from_string(response)
        self.update_token_usage(prompt_tokens, completion_tokens)

        # Print token usage statistics
        usage = self.get_token_usage()
        print("\nToken Usage Statistics:")
        print(f"Prompt Tokens: {usage['prompt_tokens']}")
        print(f"Completion Tokens: {usage['completion_tokens']}")
        print(f"Total Tokens: {usage['total_tokens']}")
        print(f"Estimated Cost: {usage['total_cost']}")