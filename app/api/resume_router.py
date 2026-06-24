from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.resume_service import ResumeService

from app.schemas.common_schema import ApiResponse, success_response, fail_response
from app.schemas.resume_schema import ResumeRequest, ResumeResponse

from app.db.database import get_db


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

resume_service = ResumeService()


# {
#   "title": "김남준 경력기술서",
#   "content": "Java/Spring Boot 기반 8년차 백엔드 개발자. 운영 효율화와 자동화 중심의 개발 경험을 보유하고 있다. 2,000대 이상 서버의 SSH/SFTP 키를 중앙에서 관리하는 UKM 시스템을 설계하고 구축했으며, 비동기 대량 요청을 Batch와 Job 단위로 나누어 처리하는 구조를 직접 설계했다. Spring Scheduler 기반 폴링 구조를 구현하여 미완료 작업을 주기적으로 추적하고, 타임아웃이 발생한 작업은 별도로 분리해 처리했다. Messenger와 Mail 연동을 위한 공통 API를 설계해 사내 여러 프로젝트에 제공했으며, AOP 기반의 공통 로그 및 응답 처리 구조를 적용했다. Zero Trust 보안 아키텍처 환경에서 AD와 SASE 연동 기반의 권한 자동 등록 및 삭제 기능을 개발했고, Splunk 로그를 수신해 DB에 적재하고 차단 정책을 자동으로 처리하는 기능을 구현했다. 또한 Node.js와 Express.js 기반의 리워드형 SNS 앱 백엔드를 설계했으며, 일일 랭킹 집계와 포인트 자동 지급 스케줄러를 구현했다. 인수인계 받은 프로젝트에서 피드 로딩 속도가 10초 이상 걸리는 성능 문제를 발견하고, DB 쿼리 튜닝과 인덱스 정비, 이미지 압축 최적화를 통해 1초 이내로 단축시켰다. 강북삼성병원 온라인 근로계약 시스템을 설계하면서, 기획자 없이 인사담당자와 직접 소통하며 요구사항을 정의하고 전자계약 프로세스를 처음부터 끝까지 구축한 경험도 있다. 비동기 작업의 상태를 추적하고 관리하는 구조를 여러 프로젝트에서 반복적으로 설계해왔으며, 장애 상황에서 원인을 추적하고 안정적으로 복구하는 운영 자동화에 강점이 있다. AWS Architecture 교육을 수료했고, 최근에는 AI 서비스 개발로 전환하기 위해 Python과 LLM 기반 에이전트 시스템을 학습하고 있다."
# }
@router.post("", response_model=ApiResponse)
def create_resume(payload: ResumeRequest, db: Session = Depends(get_db)):
    result: ResumeResponse = resume_service.create_resume(db, payload)
    return success_response(data=result.model_dump(), message="resume created")

@router.get("/{resume_id}", response_model=ApiResponse)
def get_resume(resume_id: UUID, db: Session = Depends(get_db)):
    resume: ResumeResponse | None = resume_service.get_resume(db, resume_id)

    if resume is None:
        raise HTTPException(status_code=404, detail="resume not found")
    
    return success_response(data=resume.model_dump(), message="resume fetched")