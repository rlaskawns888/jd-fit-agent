from fastapi import FastAPI

from app.api.analysis_router import router as analysis_router
from app.api.health_router import router as health_router
from app.api.resume_router import router as reasume_router

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.database import Base, engine


Base.metadata.create_all(bind=engine)
# [TEST] SQLAlchemy 모델 기준으로 테이블을 자동 생성

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name, 
        debug=settings.debug,
        version=settings.api_version,
    )

    register_exception_handlers(app)

    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(analysis_router, prefix=settings.api_v1_prefix)
    app.include_router(reasume_router, prefix=settings.api_v1_prefix)
    
    return app


app = create_app()
