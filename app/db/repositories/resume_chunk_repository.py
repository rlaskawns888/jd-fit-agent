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

    def find_similar(
            self, 
            db:Session, 
            query_embedding: list[float], 
            resume_id: Optional[UUID] = None,
            limit: int = 5,
    ) -> list[ResumeChunk]:
        """
        query_embedding과 코사인 거리가 가까운 순으로 chunk를 limit개 반환한다.
        resume_id를 주면 특정 이력서 안에서만 검색한다.
        """
        query = db.query(ResumeChunk)

        if resume_id is not None:
            query = query.filter(ResumeChunk.resume_id == resume_id)

        return (
            query.order_by(ResumeChunk.embedding.cosine_distance(query_embedding))
             .limit(limit)
             .all()
        )