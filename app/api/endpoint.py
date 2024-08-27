from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from app.service.interview_service import InterviewService
from app.core.config import settings
from app.core.auth import validate_token, create_access_token
from pydantic import BaseModel
from jose import JWTError

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

interview_service = InterviewService()

class CreateInterviewRequest(BaseModel):
    resume: str  # base64 encoded resume file
    job_description: str
    model: str = "claude-3-sonnet-20240229"

class CandidateMessageRequest(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return validate_token(token)
    except JWTError:
        raise credentials_exception

@router.post("/token")
async def login(request: LoginRequest):
    # In a real application, you would verify the username and password against a database
    if request.username == "testuser" and request.password == "testpassword":
        access_token = create_access_token(data={"sub": request.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/v1/interviews")
async def create_interview_session(
    request: CreateInterviewRequest, 
    current_user: str = Depends(get_current_user)
):
    try:
        session_id = await interview_service.create_session(request.resume, request.job_description, request.model)
        return {"session_id": session_id, "message": "Interview session created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create interview session: {str(e)}")

@router.post("/v1/interviews/{session_id}/start")
async def start_interview(
    session_id: str, 
    current_user: str = Depends(get_current_user)
):
    try:
        initial_message = await interview_service.start_interview(session_id)
        return initial_message
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@router.post("/v1/interviews/{session_id}/messages")
async def send_candidate_message(
    session_id: str, 
    request: CandidateMessageRequest, 
    current_user: str = Depends(get_current_user)
):
    try:
        response = await interview_service.process_candidate_message(session_id, request.message)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.post("/v1/interviews/{session_id}/end")
async def end_interview(
    session_id: str, 
    current_user: str = Depends(get_current_user)
):
    try:
        summary = await interview_service.end_interview(session_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end interview: {str(e)}")

@router.get("/v1/interviews/{session_id}/transcript")
async def get_interview_transcript(
    session_id: str, 
    current_user: str = Depends(get_current_user)
):
    try:
        transcript = await interview_service.get_transcript(session_id)
        return {"transcript": transcript}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve transcript: {str(e)}")

@router.get("/v1/interviews/{session_id}/statistics")
async def get_interview_statistics(
    session_id: str, 
    current_user: str = Depends(get_current_user)
):
    try:
        statistics = interview_service.get_statistics(session_id)
        return statistics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")