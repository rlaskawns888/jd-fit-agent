from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.resume_schema import ResumeRequest, ResumeResponse

from app.db.repositories.resume_repository import ResumeRepository
from app.db.repositories.resume_chunk_repository import ResumeChunkRepository

from app.services.embedding_service import EmbeddingService

from app.db.models import Resume, ResumeChunk

from app.utils.text_chunker import split_into_chunks

from app.core.config import settings

class ResumeService:
    def __init__(self):
        self.resume_repository = ResumeRepository()
        self.resume_chunk_repository = ResumeChunkRepository()
        self.embedding_service = EmbeddingService()

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
        
        # 이력서 원문을 chunk로 쪼개서 임베딩까지 만들어 저장한다.
        # 이게 없으면 이력서는 DB에는 있지만 RAG 검색 대상이 되지 못한다.
        self._create_chunks(db, saved_resume)

        return self._to_response(saved_resume)
    
    def _create_chunks(self, db: Session, resume: Resume) -> None:
        texts = split_into_chunks(
            resume.content,
            chunk_size=settings.resume_chunk_size,
            overlap=settings.resume_chunk_overlap,
        )

        if not texts:
            return
        
        # OpenAI 호출은 한 번만 (여러 chunk를 배치로 묶어서 보냄)
        embeddings = self.embedding_service.embed_texts(texts)

        chunks = [
            ResumeChunk(
                resume_id=resume.resume_id,
                chunk_index=index,
                source=text,
                embedding=embedding,
                token_count=None,
            )
            for index, (text, embedding) in enumerate(zip(texts, embeddings))
        ]

        self.resume_chunk_repository.insert_chunks(db, chunks)
        db.commit()

    
    def get_resume(self, db: Session, resume_id: UUID) -> Optional[ResumeResponse]:
        resume = self.resume_repository.find_by_id(db, resume_id)
        if resume is None:
            return None
        
        return self._to_response(resume)