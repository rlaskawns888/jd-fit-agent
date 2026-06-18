from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

#create_engine: 파이썬 코드와 실제 데이터베이스(PostgreSQL, MySQL 등) 사이의 연결 다리를 만드는 객체입니다.
#declarative_base: 데이터베이스 테이블을 파이썬 클래스로 정의할 수 있게 해주는 기초 클래스를 생성합니다.
#sessionmaker: 데이터베이스와 상호작용하는 '세션' 객체를 생성하는 공장(Factory) 역할을 합니다.

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
#데이터베이스의 테이블과 매핑될 파이썬 클래스를 만들 때, 
# 이 Base 클래스를 상속받아야 합니다. 
# 이렇게 하면 SQLAlchemy가 파이썬 클래스만 보고도 데이터베이스 테이블 구조를 파악할 수 있습니다.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()