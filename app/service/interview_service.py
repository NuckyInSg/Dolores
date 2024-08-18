from app.agent.software_agent import SoftwareInterviewAgent
from app.tools.document_parser import parse_resume, parse_job_description
from app.core.config import settings
from app.llm.llm_factory import create_llm
import base64
import uuid
from typing import Dict, List
import os

class InterviewService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sessions: Dict[str, SoftwareInterviewAgent] = {}
        self.transcripts: Dict[str, List[Dict[str, str]]] = {}
        self.statistics: Dict[str, Dict[str, int]] = {}

    async def create_session(self, resume_base64: str, job_description: str, model: str) -> str:
        if model not in settings.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model}")

        session_id = str(uuid.uuid4())
        
        # Decode resume
        resume_content = base64.b64decode(resume_base64).decode('utf-8')
        
        # Parse resume and job description
        parsed_resume = parse_resume(resume_content)
        parsed_job_description = parse_job_description(job_description)

        # Get model configuration
        model_config = settings.SUPPORTED_MODELS[model]

        # Create LLM
        llm = create_llm(
            name=model_config["name"],
            api_key=getattr(settings, model_config["api_key"]),
            api_url=getattr(settings, model_config["api_url"]),
            temperature=model_config["temperature"]
        )

        # Create agent
        agent = SoftwareInterviewAgent(llm, parsed_resume, parsed_job_description)
        self.sessions[session_id] = agent
        self.transcripts[session_id] = []
        self.statistics[session_id] = {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0}

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
        self._update_statistics(session_id, response["token_usage"])
        
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
        self._update_statistics(session_id, response["token_usage"])
        
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
        self._update_statistics(session_id, response["token_usage"])
        
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
        if session_id not in self.statistics:
            raise ValueError("Invalid session ID")
        
        stats = self.statistics[session_id]
        total_tokens = stats["total_tokens"]
        return {
            "total_tokens": total_tokens,
            "input_tokens": stats["input_tokens"],
            "output_tokens": stats["output_tokens"],
            "context_percentage": (total_tokens / 200000) * 100,  # Assuming 200k token context window
            "estimated_cost": (total_tokens / 1000) * 0.01  # Assuming $0.01 per 1k tokens
        }

    def _update_statistics(self, session_id: str, token_usage: Dict[str, int]):
        stats = self.statistics[session_id]
        stats["input_tokens"] += token_usage["prompt_tokens"]
        stats["output_tokens"] += token_usage["completion_tokens"]
        stats["total_tokens"] = stats["input_tokens"] + stats["output_tokens"]