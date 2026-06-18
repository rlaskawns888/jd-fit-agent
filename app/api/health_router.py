from fastapi import APIRouter

from app.core.config import settings

from app.schemas.common_schema import ApiResponse, success_response


router = APIRouter(
    tags=["Health"]
)


@router.get("/health", response_model=ApiResponse)
async def health_check() -> ApiResponse:
    return success_response(
        data={
            "service": "JD Fit Agent",
            "status": "UP",
        }
    )

