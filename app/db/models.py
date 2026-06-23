import uuid

from sqlalchemy import ForeignKey, Column, DateTime, Integer, String, Text, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.db.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    resume_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False, default="MARKDOWN")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    chunks = relationship("ResumeChunk", back_populates="resume", cascade="all, delete-orphan")

class ResumeChunk(Base):
    __tablename__ = "resume_chunks"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    source = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    resume = relationship("Resume", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint("resume_id", "chunk_index", name="uq_resume_chunks_resume_id_chunk_index"),
        Index("ix_resume_chunks_embedding_hnsw", "embedding", postgresql_using="hnsw", postgresql_ops={"embedding": "vector_cosine_ops"},)
    )
