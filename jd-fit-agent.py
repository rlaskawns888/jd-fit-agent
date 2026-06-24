from app.db.database import SessionLocal
from app.db.models import ResumeChunk
from app.services.embedding_service import EmbeddingService
from app.db.repositories.resume_chunk_repository import ResumeChunkRepository

db = SessionLocal()
resume_id = "2aef9094-b10c-4faf-abcc-6fec6d2724e6"

embedding_service = EmbeddingService()
query_embedding = embedding_service.embed_text("LLM 활용 경험 RAG 활용 경험")

print("query_embedding length:", len(query_embedding))

# resume_id 필터 없이 전체에서 검색
repo = ResumeChunkRepository()
results_no_filter = repo.find_similar(db, query_embedding, resume_id=None, limit=5)
print("필터 없이 검색 결과 개수:", len(results_no_filter))

# resume_id 필터를 걸고 검색 (str로)
from uuid import UUID
results_with_filter = repo.find_similar(db, query_embedding, resume_id=UUID(resume_id), limit=5)
print("resume_id 필터 검색 결과 개수:", len(results_with_filter))