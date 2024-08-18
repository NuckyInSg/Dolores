from .base_agent import BaseAgent
from langchain_core.language_models import BaseChatModel
import re
from typing import Dict, Any

class SoftwareInterviewAgent(BaseAgent):
    def __init__(self, llm: BaseChatModel, resume_content: str, job_description_content: str):
        super().__init__(llm, resume_content, job_description_content)

    def get_prompt(self) -> str:
        return f"""
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

    def parse_response(self, response: str) -> Dict[str, Any]:
        stage = self.extract_interview_stage(response)
        interviewer_content = self.extract_interviewer_content(response)
        return {
            "stage": stage,
            "interviewer_content": interviewer_content
        }

    @staticmethod
    def extract_interviewer_content(text: str) -> str:
        pattern = r'<interviewer>(.*?)</interviewer>'
        matches = re.findall(pattern, text, re.DOTALL)
        return '\n'.join(match.strip() for match in matches)

    @staticmethod
    def extract_interview_stage(text: str) -> str:
        pattern = r'<interview_stage>(.*?)</interview_stage>'
        matches = re.findall(pattern, text, re.DOTALL)
        return '\n'.join(match.strip() for match in matches)

    async def start_interview(self, session_id: str) -> dict:
        return await self.process_message(session_id, "Start the interview with the introduction and small talk stage.")

    async def process_candidate_message(self, session_id: str, message: str) -> dict:
        return await self.process_message(session_id, f"The candidate's response: {message}\nContinue the interview based on the candidate's response.")

    async def end_interview(self, session_id: str) -> dict:
        return await self.process_message(session_id, "Provide closing remarks and explain the next steps in the hiring process.")