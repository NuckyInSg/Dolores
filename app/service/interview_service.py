from app.agent.software_agent import SoftwareInterviewAgent
from app.tools.document_parser import parse_resume, parse_job_description
from app.core.config import settings
from app.llm.llm_factory import create_llm
import base64
import uuid
from typing import Dict, List
import os

class InterviewService:
    def __init__(self):
        self.sessions: Dict[str, SoftwareInterviewAgent] = {}
        self.transcripts: Dict[str, List[Dict[str, str]]] = {}

    async def create_session(self, resume: str, job_description: str, model: str) -> str:
        if model not in settings.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model}")

        session_id = str(uuid.uuid4())
        
        # Parse resume and job description
        parsed_resume = parse_resume(resume)
        parsed_job_description = parse_job_description(job_description)

        # Get model configuration
        model_config = settings.SUPPORTED_MODELS[model]

        # Create LLM
        llm = create_llm(
            model=model_config["name"],
            api_key=getattr(settings, model_config["api_key"]),
            api_url=getattr(settings, model_config["api_url"]),
            provider=model_config["provider"],
            extra_info=model_config["extra_info"]
        )

        # Create agent
        agent = SoftwareInterviewAgent(llm, parsed_resume, parsed_job_description)
        self.sessions[session_id] = agent
        self.transcripts[session_id] = []
        
        return session_id

    async def start_interview(self, session_id: str) -> Dict[str, str]:
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        agent = self.sessions[session_id]
        response = await agent.start_interview(session_id)
        
        self.transcripts[session_id].append({
            "role": "assistant", 
            "content": response["interviewer_content"], 
            "stage": response["stage"]
        })
        
        return {
            "message": {"role": "assistant", "content": response["interviewer_content"]}, 
            "stage": response["stage"]
        }

    async def process_candidate_message(self, session_id: str, message: str) -> Dict[str, str]:
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        agent = self.sessions[session_id]
        self.transcripts[session_id].append({"role": "human", "content": message})
        
        response = await agent.process_candidate_message(session_id, message)
        
        self.transcripts[session_id].append({
            "role": "assistant", 
            "content": response["interviewer_content"], 
            "stage": response["stage"]
        })
        
        return {
            "message": {"role": "assistant", "content": response["interviewer_content"]}, 
            "stage": response["stage"]
        }

    async def end_interview(self, session_id: str) -> Dict[str, str]:
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        agent = self.sessions[session_id]
        response = await agent.end_interview(session_id)
        
        self.transcripts[session_id].append({
            "role": "assistant", 
            "content": response["interviewer_content"], 
            "stage": "closing"
        })
        
        stats = self.get_statistics(session_id)
        
        return {
            "summary": response["interviewer_content"],
            "next_steps": "The interviewer will review your performance and get back to you soon.",
            "statistics": stats
        }

    def get_transcript(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self.transcripts:
            raise ValueError("Invalid session ID")
        return self.transcripts[session_id]

    def get_statistics(self, session_id: str) -> Dict[str, float]:
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")
        
        agent = self.sessions[session_id]
        token_usage = agent.get_token_usage()
        model = agent.llm.model

        return {
            "total_tokens": token_usage["total_tokens"],
            "input_tokens": token_usage["input_tokens"],
            "output_tokens": token_usage["output_tokens"],
            "context_percentage": token_usage["context_percentage"],
            "estimated_cost": token_usage["total_cost"]
        }