import tiktoken
from .base_agent import BaseAgent
from langchain_core.language_models import BaseChatModel


class SoftwareInterviewAgent(BaseAgent):
    def __init__(self, llm: BaseChatModel, resume_content: str, job_description_content: str):
        super().__init__(llm, resume_content, job_description_content)

    def get_prompt(self):
        prompt = f"""
        You are an expert IT manager conducting a job interview for a software engineering position. You have access to the candidate's resume and the job description. Conduct a realistic and professional interview following these stages:

        1. Introduction and small talk, interview_stage = introduction
        2. Overview of the candidate's background, interview_stage = overview
        3. Technical questions related to the job requirements, interview_stage = technical
        4. Project or experience deep dive, interview_stage = project
        5. Company and role-specific questions, interview_stage = company
        6. Candidate's questions for the interviewer, interview_stage = candidate
        7. Closing remarks, interview_stage = closing

        Throughout the interview, maintain a professional and friendly tone. Ask relevant questions based on the resume and job requirements. Provide thoughtful responses and follow-up questions based on the candidate's answers.

        Use the following format for each stage:
        <interview_stage>
        [Name of the stage]
        </interview_stage>

        <interviewer>
        [Your question or statement]
        </interviewer>

        Resume:
        {self.resume_content}

        Job Description:
        {self.job_description_content}

        Remember to adapt your questions and conversation based on the candidate's responses and ensure technical questions are appropriate for the position level.
        """
        return prompt

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self.llm.model_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    async def conduct_interview(self, session_id: str, user_input: str = None) -> dict:
        if user_input is None:
            # Start the interview
            input_text = "Start the interview with the introduction and small talk stage."
        else:
            input_text = f"The candidate's response: {user_input}\nContinue the interview based on the current stage and the candidate's response."

        return await self._call_llm(session_id, input_text)