from app.agent.software_agent import SoftwareInterviewAgent
from .job_description_service import DocumentService
import os

class InterviewService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.document_service = DocumentService()

    async def start_interview(self, resume_path: str, job_description_path: str, session_id: str):
        resume_content = self.document_service.parse_resume(resume_path)
        job_description_content = self.document_service.parse_job_description(job_description_path)
        
        agent = SoftwareInterviewAgent(
            self.api_key, 
            resume_content, 
            job_description_content
        )
        return await agent.conduct_interview(session_id)

    # 可以添加其他与面试流程相关的方法