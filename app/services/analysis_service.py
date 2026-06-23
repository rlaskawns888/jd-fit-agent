from uuid import uuid4

from app.agent.graph import jd_fit_graph
from app.schemas.analysis_schema import AnalysisRequest, AnalysisResponse

class AnalysisService:
    def analyze(self, payload: AnalysisRequest) -> AnalysisResponse:
        jd_text = payload.jd_text or "" 

        result = jd_fit_graph.invoke({
            "jd_text": jd_text,
            "resume_id": str(payload.resume_id) if payload.resume_id else None,
            "visited_nodes": [],
        })

        # 그래프가 어느 경로로 갔는지(visited_nodes)를 used_tools로 그대로 노출.
        # 이게 "에이전트가 실제로 도구/노드를 선택했다"는 증거가 되는 필드.
        used_tools = result.get("visited_nodes", [])

        # request_clarification으로 빠졌으면 jd_summary가 없고 안내 메시지만 있다.
        recommended_strategy = (
            result.get("clarification_message")
            or result.get("jd_summary")
            or ""
        )

        return AnalysisResponse(
            analysis_id=str(uuid4()),
            report_id=str(uuid4()),
            job_title="Unknown",  # JD 구조화 분석은 다음 단계에서 연결
            company_name="Unknown",
            fit_score=0,  # 갭 분석은 아직 미구현 단계
            strengths=[],
            gaps=[],
            matched_experiences=[],
            recommended_strategy=recommended_strategy,
            cover_letter_draft="",
            interview_questions=[],
            used_tools=used_tools,
            sources=[],
        )

