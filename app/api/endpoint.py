from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from typing import Optional
from app.service.resume_service import ResumeService
from app.service.job_description_service import JobDescriptionService
from app.service.interview_service import InterviewService
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()

class CreateInterviewRequest(BaseModel):
    resume: str  # base64 encoded resume file
    job_description: str
    model: str = "claude-3-sonnet-20240229"

class CandidateMessageRequest(BaseModel):
    message: str

@router.post("/v1/interviews")
async def create_interview_session(request: CreateInterviewRequest, authorization: str = Header(...)):
    # TODO: Implement authentication check
    interview_service = InterviewService(api_key=settings.ANTHROPIC_API_KEY)
    session_id = await interview_service.create_session(request.resume, request.job_description, request.model)
    return {"session_id": session_id, "message": "Interview session created successfully"}

@router.post("/v1/interviews/{session_id}/start")
async def start_interview(session_id: str, authorization: str = Header(...)):
    # TODO: Implement authentication check
    interview_service = InterviewService(api_key=settings.ANTHROPIC_API_KEY)
    initial_message = await interview_service.start_interview(session_id)
    return initial_message

@router.post("/v1/interviews/{session_id}/messages")
async def send_candidate_message(session_id: str, request: CandidateMessageRequest, authorization: str = Header(...)):
    # TODO: Implement authentication check
    interview_service = InterviewService(api_key=settings.ANTHROPIC_API_KEY)
    response = await interview_service.process_candidate_message(session_id, request.message)
    return response

@router.post("/v1/interviews/{session_id}/end")
async def end_interview(session_id: str, authorization: str = Header(...)):
    # TODO: Implement authentication check
    interview_service = InterviewService(api_key=settings.ANTHROPIC_API_KEY)
    summary = await interview_service.end_interview(session_id)
    return summary

@router.get("/v1/interviews/{session_id}/transcript")
async def get_interview_transcript(session_id: str, authorization: str = Header(...)):
    # TODO: Implement authentication check
    interview_service = InterviewService(api_key=settings.ANTHROPIC_API_KEY)
    transcript = await interview_service.get_transcript(session_id)
    return {"transcript": transcript}

@router.get("/v1/interviews/{session_id}/statistics")
async def get_interview_statistics(session_id: str, authorization: str = Header(...)):
    # TODO: Implement authentication check
    interview_service = InterviewService(api_key=settings.ANTHROPIC_API_KEY)
    statistics = await interview_service.get_statistics(session_id)
    return statistics