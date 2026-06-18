from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.resume_schema import ResumeRequest, ResumeResponse

from app.db.repositories.resume_repository import ResumeRepository

from app.db.models import Resume

class ResumeService:
    def __init__(self):
        self.resume_repository = ResumeRepository()

    def _to_response(self, resume: Resume) -> ResumeResponse:
        return ResumeResponse.model_validate(
            {
                "resume_id": resume.resume_id,
                "title": resume.title,
                "content": resume.content,
                "source_type": resume.source_type,
                "created_at": resume.created_at,
                "updated_at": resume.updated_at,
            }
        )

    def create_resume(self, db: Session, payload: ResumeRequest) -> ResumeResponse:
        resume = Resume(
            title=payload.title,
            content=payload.content,
            source_type="MARKDOWN",
        )
        saved_resume = self.resume_repository.save(db, resume)
        return self._to_response(saved_resume)
    
    def get_resume(self, db: Session, resume_id: UUID) -> Optional[ResumeResponse]:
        resume = self.resume_repository.find_by_id(db, resume_id)
        if resume is None:
            return None
        
        return self._to_response(resume)