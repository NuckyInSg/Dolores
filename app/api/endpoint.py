from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.service.resume_service import ResumeService
from app.service.job_description_service import JobDescriptionService
from app.service.interview_service import InterviewService
from app.core.config import settings

router = APIRouter()

@router.post("/resumes")
async def upload_resume(file: UploadFile = File(...)):
    resume_service = ResumeService()
    result = await resume_service.upload_resume(file)
    return {"message": "Resume uploaded and parsed successfully", "data": result}

@router.post("/job-descriptions")
async def upload_job_description(file: UploadFile = File(...)):
    job_description_service = JobDescriptionService()
    result = await job_description_service.upload_job_description(file)
    return {"message": "Job description uploaded and parsed successfully", "data": result}

@router.post("/interviews")
async def start_interview(resume_content: str, job_description_content: str, session_id: str):
    interview_service = InterviewService(api_key=settings.ANTHROPIC_API_KEY)
    result = await interview_service.start_interview(resume_content, job_description_content, session_id)
    return {"message": "Interview completed", "data": result}