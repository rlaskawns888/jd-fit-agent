from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Resume

class ResumeRepository:
    def save(self, db: Session, resume: Resume):
        db.add(resume)
        db.commit();
        db.refresh(resume)
        return resume
    
    def find_by_id(self, db:Session, resume_id: UUID) -> Optional[Resume]:
        return db.query(Resume).filter(Resume.resume_id == resume_id).one_or_none()
