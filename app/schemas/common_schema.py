from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = Field(description="request succeeded")
    code: str = Field(description="status code")
    message: str = Field(description="message")
    data: Any | None = Field(default=None, description="Response payload")


def success_response(data: Any | None = None, message: str = "success") -> dict[str, Any]:
    return ApiResponse(
        success=True,
        code="200",
        message=message,
        data=data,
    ).model_dump()


def fail_response(code: str, message: str, data: Any | None = None) -> dict[str, Any]:
    return ApiResponse(
        success=False,
        code=code,
        message=message,
        data=data,
    ).model_dump()

