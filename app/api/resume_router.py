from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.resume_service import ResumeService

from app.schemas.common_schema import ApiResponse, success_response, fail_response
from app.schemas.resume_schema import ResumeRequest, ResumeResponse

from app.db.database import get_db


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

resume_service = ResumeService()

@router.post("", response_model=ApiResponse)
def create_resume(payload: ResumeRequest, db: Session = Depends(get_db)):
    result: ResumeResponse = resume_service.create_resume(db, payload)
    return success_response(data=result.model_dump(), message="resume created")

@router.get("/{resume_id}", response_model=ApiResponse)
def get_resume(resume_id: UUID, db: Session = Depends(get_db)):
    resume: ResumeResponse | None = resume_service.get_resume(db, resume_id)

    if resume is None:
        raise HTTPException(status_code=404, detail="resume not found")
    
    return success_response(data=resume.model_dump(), message="resume fetched")