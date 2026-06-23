from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ResumeChunk

class ResumeChunkRepository:
    def insert_chunks(self, db:Session, chunks: list[ResumeChunk]) -> list[ResumeChunk]:
        db.add_all(chunks)
        db.flush()

        for chunk in chunks:
            db.refresh(chunk)
        
        return chunks
    

    def delete_chunk(self, db:Session, resume_id: UUID) -> None:
        (
            db.query(ResumeChunk)
             .filter(ResumeChunk.resume_id == resume_id)
             .delete(synchronize_session=False)
        )
