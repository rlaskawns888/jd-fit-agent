from fastapi import APIRouter

from app.core.config import settings

from app.schemas.common_schema import ApiResponse, success_response


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("", response_model=ApiResponse)
async def health_check() -> ApiResponse:
    return success_response(
        data={
            "service": "JD Fit Agent",
            "status": "UP",
        }
    )

