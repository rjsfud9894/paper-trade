from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User
from models import Stock
from models import Trade
from services import AuthService


router = APIRouter(prefix="/portfolio", tags=["포트폴리오"])


# 응답 데이터 형식
class HoldingDetail(BaseModel):
    symbol: str
    name: str
    quantity: int
    avg_price: float
    total_invested: float


class PortfolioResponse(BaseModel):
    balance: float
    total_invested: float
    total_assets: float
    holdings: list[HoldingDetail]


# 토큰에서 유저 가져오는 함수
def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다"
        )
    
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저를 찾을 수 없습니다"
        )
    
    return user


# 포트폴리오 요약 조회
@router.get("/summary", response_model=PortfolioResponse)
def get_portfolio_summary(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    
    # 모든 주식 가져오기
    stocks = db.query(Stock).all()
    
    holdings = []
    total_invested = 0
    
    for stock in stocks:
        # 매수 합계
        buy_quantity = db.query(func.sum(Trade.quantity)).filter(
            Trade.user_id == user.id,
            Trade.stock_id == stock.id,
            Trade.trade_type == "buy"
        ).scalar() or 0
        
        # 매도 합계
        sell_quantity = db.query(func.sum(Trade.quantity)).filter(
            Trade.user_id == user.id,
            Trade.stock_id == stock.id,
            Trade.trade_type == "sell"
        ).scalar() or 0
        
        # 보유 수량
        quantity = buy_quantity - sell_quantity
        
        if quantity > 0:
            # 평균 매수가 계산
            buy_trades = db.query(Trade).filter(
                Trade.user_id == user.id,
                Trade.stock_id == stock.id,
                Trade.trade_type == "buy"
            ).all()
            
            total_cost = sum(t.price * t.quantity for t in buy_trades)
            total_buy_quantity = sum(t.quantity for t in buy_trades)
            avg_price = total_cost / total_buy_quantity if total_buy_quantity > 0 else 0
            
            # 현재 보유 가치 (평균 매수가 기준)
            invested = quantity * avg_price
            total_invested += invested
            
            holdings.append(HoldingDetail(
                symbol=stock.symbol,
                name=stock.name,
                quantity=quantity,
                avg_price=avg_price,
                total_invested=invested
            ))
    
    return PortfolioResponse(
        balance=user.balance,
        total_invested=total_invested,
        total_assets=user.balance + total_invested,
        holdings=holdings
    )
