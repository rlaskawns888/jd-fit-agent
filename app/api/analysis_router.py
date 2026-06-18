from fastapi import APIRouter

from app.core.config import settings

from app.schemas.common_schema import ApiResponse, success_response
from app.schemas.analysis_schema import AnalysisRequest, AnalysisResponse

from app.services.analysis_service import AnalysisService

router = APIRouter(
    tags=["Analysis"]
)

analysis_service = AnalysisService()


@router.post("/run", response_model=ApiResponse)
async def analyze_job_description(payload: AnalysisRequest) -> ApiResponse:
    result: AnalysisResponse = analysis_service.analyze(payload)
    return success_response(data=result.model_dump())

