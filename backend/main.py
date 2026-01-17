from fastapi import FastAPI

app = FastAPI(
    title="Paper Trade API",
    description="주식 모의 거래 연습 API",
    version="0.1.0"
)

@app.get("/")
def home():
    return {"message": "Paper Trade API에 오신 것을 환영합니다!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
