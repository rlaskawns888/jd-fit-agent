from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class ResumeRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="제목")
    content: str = Field(..., min_length=10, description="본문")


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    #ORM 객체에서 바로 만들 수 있게 해주는 설정

    resume_id: UUID
    title: str
    content: str
    source_type: str
    created_at: datetime
    updated_at: datetime