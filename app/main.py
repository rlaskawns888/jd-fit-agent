from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis_router import router as analysis_router
from app.api.health_router import router as health_router
from app.api.resume_router import router as reasume_router

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.database import Base, engine, init_db

# DB초기화
init_db()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name, 
        debug=settings.debug,
        version=settings.api_version,
    )

    # React 개발 서버(5173)에서 오는 요청을 허용
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(analysis_router, prefix=settings.api_v1_prefix)
    app.include_router(reasume_router, prefix=settings.api_v1_prefix)
    
    return app


app = create_app()
