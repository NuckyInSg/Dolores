from app.agent.software_agent import SoftwareInterviewAgent
from app.tools.document_parser import parse_resume, parse_job_description
import os
import base64
import uuid
from typing import Dict, List

class InterviewService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sessions: Dict[str, SoftwareInterviewAgent] = {}
        self.transcripts: Dict[str, List[Dict[str, str]]] = {}
        self.statistics: Dict[str, Dict[str, int]] = {}

    async def create_session(self, resume_base64: str, job_description: str, model: str) -> str:
        session_id = str(uuid.uuid4())
        
        # Decode and save resume
        resume_content = base64.b64decode(resume_base64).decode('utf-8')
        resume_path = f"temp_resume_{session_id}.txt"
        with open(resume_path, 'w') as f:
            f.write(resume_content)

        # Save job description
        job_description_path = f"temp_jd_{session_id}.txt"
        with open(job_description_path, 'w') as f:
            f.write(job_description)

        # Create agent
        agent = SoftwareInterviewAgent(self.api_key, resume_path, job_description_path, model=model)
        self.sessions[session_id] = agent
        self.transcripts[session_id] = []
        self.statistics[session_id] = {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0}

        # Clean up temporary files
        os.remove(resume_path)
        os.remove(job_description_path)

        return session_id

    async def start_interview(self, session_id: str) -> Dict[str, str]:
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        agent = self.sessions[session_id]
        response = await agent.interview_chain.ainvoke(
            {"input": "Start the interview with the introduction and small talk stage."},
            config={"configurable": {"session_id": session_id}}
        )
        
        interviewer_content = agent.extract_interviewer_content(response)
        stage = agent.extract_interview_stage(response)
        
        self.transcripts[session_id].append({"role": "assistant", "content": interviewer_content, "stage": stage})
        self._update_statistics(session_id, len("Start the interview"), len(response))
        
        return {"message": {"role": "assistant", "content": interviewer_content}, "stage": stage}

    async def process_candidate_message(self, session_id: str, message: str) -> Dict[str, str]:
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        agent = self.sessions[session_id]
        self.transcripts[session_id].append({"role": "human", "content": message})
        
        response = await agent.interview_chain.ainvoke(
            {"input": f"The candidate's response: {message}\nContinue the interview based on the candidate's response."},
            config={"configurable": {"session_id": session_id}}
        )
        
        interviewer_content = agent.extract_interviewer_content(response)
        stage = agent.extract_interview_stage(response)
        
        self.transcripts[session_id].append({"role": "assistant", "content": interviewer_content, "stage": stage})
        self._update_statistics(session_id, len(message), len(response))
        
        return {"message": {"role": "assistant", "content": interviewer_content}, "stage": stage}

    async def end_interview(self, session_id: str) -> Dict[str, str]:
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        agent = self.sessions[session_id]
        response = await agent.interview_chain.ainvoke(
            {"input": "Provide closing remarks and explain the next steps in the hiring process."},
            config={"configurable": {"session_id": session_id}}
        )
        
        interviewer_content = agent.extract_interviewer_content(response)
        self.transcripts[session_id].append({"role": "assistant", "content": interviewer_content, "stage": "closing"})
        self._update_statistics(session_id, len("Provide closing remarks"), len(response))
        
        stats = self.get_statistics(session_id)
        
        return {
            "summary": interviewer_content,
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

    def _update_statistics(self, session_id: str, input_length: int, output_length: int):
        stats = self.statistics[session_id]
        stats["input_tokens"] += input_length
        stats["output_tokens"] += output_length
        stats["total_tokens"] = stats["input_tokens"] + stats["output_tokens"]