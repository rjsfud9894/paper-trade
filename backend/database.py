import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env 파일 읽기
load_dotenv()

# 환경변수에서 DB 정보 가져오기
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# DB 연결 주소
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"

# 엔진 생성 (DB와 연결하는 통로)
engine = create_engine(DATABASE_URL)

# 세션 생성 (DB와 대화하는 창구)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 부모 클래스
Base = declarative_base()

# DB 세션 가져오는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
