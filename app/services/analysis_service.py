from uuid import uuid4

from sqlalchemy.orm import Session

from app.agent.graph import build_jd_fit_graph
from app.schemas.analysis_schema import AnalysisRequest, AnalysisResponse

from app.tools.jd_crawl_tool import crawl_jd_text

class AnalysisService:
    def analyze(self, db: Session, payload: AnalysisRequest) -> AnalysisResponse:
        if payload.jd_url:
            jd_text = crawl_jd_text(payload.jd_url) #크롤링
        else:
            jd_text = payload.jd_text or ""

        graph = build_jd_fit_graph(db)
        result = graph.invoke({
            "jd_text": jd_text,
            "resume_id": str(payload.resume_id) if payload.resume_id else None,
            "visited_nodes": [],
            "retry_count": 0,
        })

        # 그래프가 어느 경로로 갔는지(visited_nodes)를 used_tools로 그대로 노출.
        # 이게 "에이전트가 실제로 도구/노드를 선택했다"는 증거가 되는 필드.
        used_tools = result.get("visited_nodes", [])
        jd_summary = result.get("jd_summary")
        matched_chunks = result.get("matched_chunks", [])

        if result.get("clarification_message"):
            recommended_strategy = result["clarification_message"]
            job_title = "Unknown"
            company_name = "Unknown"
        elif jd_summary:
            recommended_strategy = f"필수기술: {', '.join(jd_summary.get('required_skills', []))}"
            job_title = jd_summary.get("job_title", "Unknown")
            company_name = jd_summary.get("company_name", "Unknown")
        else:
            recommended_strategy = ""
            job_title = "Unknown"
            company_name = "Unknown"

        # 검색된 chunk 내용을 matched_experiences로 노출 (다음 단계 갭 분석의 입력 재료)
        matched_experiences = [chunk["content"] for chunk in matched_chunks]
        sources = [chunk["chunk_id"] for chunk in matched_chunks]

        return AnalysisResponse(
            analysis_id=str(uuid4()),
            report_id=str(uuid4()),
            job_title=job_title,
            company_name=company_name,
            fit_score=result.get("fit_score", 0),
            strengths=result.get("strengths", []),
            gaps=result.get("gaps", []),
            matched_experiences=matched_experiences,
            recommended_strategy=recommended_strategy,
            cover_letter_draft="",
            interview_questions=[],
            used_tools=used_tools,
            sources=sources,
            retry_count=result.get("retry_count", 0),
            resume_feedback=result.get("resume_feedback"),
        )



