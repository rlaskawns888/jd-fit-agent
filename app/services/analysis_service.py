from uuid import uuid4

from app.schemas.analysis_schema import AnalysisRequest, AnalysisResponse

class AnalysisService:
    def analyze(self, payload: AnalysisRequest) -> AnalysisResponse:
        return AnalysisResponse(
            analysis_id=str(uuid4()),
            report_id=str(uuid4()),
            job_title="Unknown",
            company_name="Unknown",
            fit_score=0,
            strengths=[],
            gaps=[],
            matched_experiences=[],
            recommended_strategy=".",
            cover_letter_draft="",
            interview_questions=[],
            used_tools=[],
            sources=[],
        )
