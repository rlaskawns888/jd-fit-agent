from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class AnalysisRequest(BaseModel):
    jd_url: Optional[str] = Field(default=None, description="채용공고URL")
    jd_text: Optional[str] = Field(default=None, description="직접 입력한 채용공고 JD")
    resume_id: Optional[UUID] = Field(default=None, description="분석에 사용할 이력서 ID")

    @model_validator(mode="after")
    def validate_jd_input(self):
        has_jd_url = self.jd_url is not None and self.jd_url.strip() != ""
        has_jd_text = self.jd_text is not None and self.jd_text.strip() != ""

        if not has_jd_url and not has_jd_text:
            raise ValueError("jd_url 또는 jd_text 중 하나는 반드시 입력해야 합니다.")

        return self


class AnalysisResponse(BaseModel):
    analysis_id: str
    report_id: str
    job_title: str
    company_name: str
    fit_score: int
    strengths: List[str]
    gaps: List[str]
    matched_experiences: List[str]
    recommended_strategy: str
    cover_letter_draft: str
    interview_questions: List[str]
    used_tools: List[str]
    sources: List[str]
    retry_count: int = 0  # 추가