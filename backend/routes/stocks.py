from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Stock
from services import StockService


router = APIRouter(prefix="/stocks", tags=["주식"])


# 응답 데이터 형식
class StockResponse(BaseModel):
    id: int
    symbol: str
    name: str

    class Config:
        from_attributes = True


class StockPriceResponse(BaseModel):
    symbol: str
    name: str
    price: float
    currency: str
    change: float
    change_percent: float


class StockCreateRequest(BaseModel):
    symbol: str
    name: str


# 전체 주식 목록 조회
@router.get("", response_model=list[StockResponse])
def get_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    return stocks


# 특정 주식 조회 (DB)
@router.get("/{symbol}", response_model=StockResponse)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주식을 찾을 수 없습니다"
        )
    return stock


# 실시간 가격 조회 (Yahoo Finance)
@router.get("/{symbol}/price", response_model=StockPriceResponse)
def get_stock_price(symbol: str):
    price_data = StockService.get_price(symbol)
    
    if price_data.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"가격 조회 실패: {price_data['error']}"
        )
    
    return StockPriceResponse(
        symbol=price_data["symbol"],
        name=price_data["name"],
        price=price_data["price"],
        currency=price_data["currency"],
        change=price_data["change"],
        change_percent=price_data["change_percent"]
    )


# 여러 주식 실시간 가격 조회
@router.get("/prices/realtime")
def get_realtime_prices(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    symbols = [stock.symbol for stock in stocks]
    
    prices = StockService.get_prices(symbols)
    return prices


# 주식 추가
@router.post("", response_model=StockResponse)
def create_stock(request: StockCreateRequest, db: Session = Depends(get_db)):
    existing = db.query(Stock).filter(Stock.symbol == request.symbol).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 종목입니다"
        )
    
    new_stock = Stock(
        symbol=request.symbol,
        name=request.name
    )
    
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    
    return new_stock
