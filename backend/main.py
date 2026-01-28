from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal
from models import Stock
from routes import auth_router
from routes import stocks_router
from routes import trades_router
from routes import portfolio_router


# 기본 주식 데이터
DEFAULT_STOCKS = [
    {"symbol": "AAPL", "name": "Apple"},
    {"symbol": "GOOGL", "name": "Google"},
    {"symbol": "TSLA", "name": "Tesla"},
    {"symbol": "MSFT", "name": "Microsoft"},
    {"symbol": "AMZN", "name": "Amazon"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작할 때 실행
    db = SessionLocal()
    try:
        for stock_data in DEFAULT_STOCKS:
            existing = db.query(Stock).filter(Stock.symbol == stock_data["symbol"]).first()
            if not existing:
                new_stock = Stock(
                    symbol=stock_data["symbol"],
                    name=stock_data["name"]
                )
                db.add(new_stock)
        db.commit()
        print("✅ 기본 주식 데이터 로드 완료!")
    finally:
        db.close()
    
    yield  # 앱 실행 중
    
    # 앱 종료할 때 실행 (필요하면 여기에 정리 코드)


app = FastAPI(
    title="Paper Trade API",
    description="모의 주식 거래 연습 API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결
app.include_router(auth_router)
app.include_router(stocks_router)
app.include_router(trades_router)
app.include_router(portfolio_router)


@app.get("/")
def read_root():
    return {"message": "Paper Trade API에 오신 것을 환영합니다!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
