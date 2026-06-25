from uuid import UUID

from sqlalchemy.orm import Session

from app.services.embedding_service import EmbeddingService

from app.db.repositories.resume_chunk_repository import ResumeChunkRepository

def search_resume_chunks(
    db: Session,
    query_text: str,
    resume_id: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """
    query_text(JD 요구사항을 합친 문장)와 의미적으로 비슷한 이력서 chunk를 찾는다.

    이 함수가 LangGraph 노드(search_resume_node)에서 "Tool"로 호출될 대상이다.
    노드 코드와 검색 로직을 분리해두면, 나중에 다른 노드(예: 갭 분석 재검색)에서도
    이 함수를 그대로 재사용할 수 있다.
    """
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.embed_text(query_text)

    # print("DEBUG (tool) resume_id param:", repr(resume_id))  # 추가
    # print("DEBUG (tool) query_embedding length:", len(query_embedding))  # 추가

    chunk_repository = ResumeChunkRepository()
    resume_uuid = UUID(resume_id) if resume_id else None

    chunks = chunk_repository.find_similar(
        db=db,
        query_embedding=query_embedding,
        resume_id=resume_uuid,
        limit=top_k,
    )

    # print("DEBUG (tool) chunks found:", len(chunks))  # 추가

    # 노드/그래프 state에는 ORM 객체를 그대로 넣지 않고 dict로 변환해서 넣는다.
    # (LangGraph state는 직렬화 가능한 값만 들고 다니는 게 안전하다.)
    return [
         {
             "chunk_id": str(chunk.chunk_id),
             "content": chunk.source,
             "chunk_index": chunk.chunk_index,
         }
         for chunk in chunks
    ]

def build_search_query_from_jd(jd_summary: dict) -> str:
    """
    JD 분석 결과(jd_summary)에서 required_skills + preferred_skills를
    하나의 검색 문장으로 합친다.

    예: {"required_skills": ["Python", "FastAPI"], "preferred_skills": ["Docker"]}
        -> "Python FastAPI Docker"

    이렇게 합치는 이유: 스킬을 하나씩 따로 검색하면 API 호출이 N번 필요하고,
    결과도 "Python"에 대한 검색, "FastAPI"에 대한 검색처럼 따로따로 나와서
    합치기가 번거롭다. 하나의 문장으로 합쳐서 한 번의 벡터 검색으로
    "이 모든 요구사항과 전반적으로 관련된" chunk를 찾는 게 더 실용적이다.
    """
    required = jd_summary.get("required_skills", []) if jd_summary else []
    preferred = jd_summary.get("preferred_skills", []) if jd_summary else []
    domain = jd_summary.get("domain", "") if jd_summary else ""

    parts = required + preferred
    if domain:
        parts.append(domain)

    return " ".join(parts)

def build_broader_search_query_from_jd(jd_summary: dict) -> str:
    """
    재시도용 검색 문장. 처음 검색(build_search_query_from_jd)보다
    domain 설명을 더 비중 있게 포함해서, 기술 키워드로는 못 찾은
    관련 경험을 더 넓게 찾아보려는 목적이다.
    """
    required = jd_summary.get("required_skills", []) if jd_summary else []
    preferred = jd_summary.get("preferred_skills", []) if jd_summary else []
    domain = jd_summary.get("domain", "") if jd_summary else ""
    job_title = jd_summary.get("job_title", "") if jd_summary else ""

    # domain과 job_title을 앞에 둬서 검색 문장에서 비중을 높인다.
    parts = [domain, job_title] + required + preferred
    return " ".join(p for p in parts if p)
