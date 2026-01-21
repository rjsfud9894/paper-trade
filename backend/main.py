from fastapi import FastAPI

from routes import auth_router
from routes import stocks_router


app = FastAPI(
    title="Paper Trade API",
    description="모의 주식 거래 연습 API",
    version="0.1.0"
)

# 라우터 연결
app.include_router(auth_router)
app.include_router(stocks_router)


@app.get("/")
def read_root():
    return {"message": "Paper Trade API에 오신 것을 환영합니다!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
