from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Stock


router = APIRouter(prefix="/stocks", tags=["주식"])


# 응답 데이터 형식
class StockResponse(BaseModel):
    id: int
    symbol: str
    name: str

    class Config:
        from_attributes = True


# 주식 추가 요청 형식 (관리자용)
class StockCreateRequest(BaseModel):
    symbol: str
    name: str


# 전체 주식 목록 조회
@router.get("", response_model=list[StockResponse])
def get_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    return stocks


# 특정 주식 조회
@router.get("/{symbol}", response_model=StockResponse)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주식을 찾을 수 없습니다"
        )
    return stock


# 주식 추가 (샘플 데이터 넣을 때 사용)
@router.post("", response_model=StockResponse)
def create_stock(request: StockCreateRequest, db: Session = Depends(get_db)):
    # 중복 확인
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
