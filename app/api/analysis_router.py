from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings

from app.schemas.common_schema import ApiResponse, success_response
from app.schemas.analysis_schema import AnalysisRequest, AnalysisResponse

from app.services.analysis_service import AnalysisService
from app.db.database import get_db

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

analysis_service = AnalysisService()

# {
#   "jd_text": "토스 AI Platform 팀에서 AI 엔지니어(Platform)를 채용합니다. 본 팀은 토스 전반의 AI 활용을 지원하며, 누구나 AI를 빠르고 안정적으로 사용할 수 있는 플랫폼과 도구를 만드는 역할을 합니다. 구체적으로 LLM 기반 컴포넌트의 재사용 플랫폼화, Agent 시스템 구축 및 실험 기반 마련, RAG·Agent의 서빙 및 운영 도구화를 담당합니다. 지원 자격으로는 LLM, RAG, Agent 등을 활용해 실제 문제를 시스템적으로 해결해 본 경험, 비동기 작업의 상태를 안정적으로 관리하고 장애 상황을 추적해 본 경험, 운영 자동화 경험이 요구됩니다.",
#   "resume_id": "77ec206e-adbe-42df-9515-2aaf762cc03f"
# }
@router.post("/run", response_model=ApiResponse)
async def analyze_job_description(payload: AnalysisRequest, db: Session = Depends(get_db)) -> ApiResponse:
    result: AnalysisResponse = analysis_service.analyze(db, payload)
    return success_response(data=result.model_dump())

