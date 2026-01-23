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


router = APIRouter(prefix="/trades", tags=["거래"])


# 요청 데이터 형식
class TradeRequest(BaseModel):
    symbol: str
    quantity: int
    price: float


# 응답 데이터 형식
class TradeResponse(BaseModel):
    id: int
    user_id: int
    stock_id: int
    trade_type: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


class HoldingResponse(BaseModel):
    symbol: str
    name: str
    quantity: int
    avg_price: float
    total_value: float


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


# 매수 API
@router.post("/buy", response_model=TradeResponse)
def buy_stock(request: TradeRequest, token: str, db: Session = Depends(get_db)):
    # 유저 확인
    user = get_current_user(token, db)
    
    # 주식 확인
    stock = db.query(Stock).filter(Stock.symbol == request.symbol).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주식을 찾을 수 없습니다"
        )
    
    # 총 금액 계산
    total_cost = request.price * request.quantity
    
    # 잔고 확인
    if user.balance < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"잔고가 부족합니다. 현재 잔고: {user.balance}원"
        )
    
    # 잔고 차감
    user.balance -= total_cost
    
    # 거래 기록 생성
    new_trade = Trade(
        user_id=user.id,
        stock_id=stock.id,
        trade_type="buy",
        quantity=request.quantity,
        price=request.price
    )
    
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    
    return new_trade


# 매도 API
@router.post("/sell", response_model=TradeResponse)
def sell_stock(request: TradeRequest, token: str, db: Session = Depends(get_db)):
    # 유저 확인
    user = get_current_user(token, db)
    
    # 주식 확인
    stock = db.query(Stock).filter(Stock.symbol == request.symbol).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주식을 찾을 수 없습니다"
        )
    
    # 보유 수량 계산
    buy_quantity = db.query(func.sum(Trade.quantity)).filter(
        Trade.user_id == user.id,
        Trade.stock_id == stock.id,
        Trade.trade_type == "buy"
    ).scalar() or 0
    
    sell_quantity = db.query(func.sum(Trade.quantity)).filter(
        Trade.user_id == user.id,
        Trade.stock_id == stock.id,
        Trade.trade_type == "sell"
    ).scalar() or 0
    
    holding_quantity = buy_quantity - sell_quantity
    
    # 보유량 확인
    if holding_quantity < request.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"보유 수량이 부족합니다. 현재 보유: {holding_quantity}주"
        )
    
    # 잔고 추가
    total_value = request.price * request.quantity
    user.balance += total_value
    
    # 거래 기록 생성
    new_trade = Trade(
        user_id=user.id,
        stock_id=stock.id,
        trade_type="sell",
        quantity=request.quantity,
        price=request.price
    )
    
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    
    return new_trade


# 거래 내역 조회
@router.get("/history", response_model=list[TradeResponse])
def get_trade_history(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    
    trades = db.query(Trade).filter(Trade.user_id == user.id).all()
    
    return trades


# 보유 주식 조회
@router.get("/holdings", response_model=list[HoldingResponse])
def get_holdings(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    
    # 모든 주식 가져오기
    stocks = db.query(Stock).all()
    
    holdings = []
    
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
            total_quantity = sum(t.quantity for t in buy_trades)
            avg_price = total_cost / total_quantity if total_quantity > 0 else 0
            
            holdings.append(HoldingResponse(
                symbol=stock.symbol,
                name=stock.name,
                quantity=quantity,
                avg_price=avg_price,
                total_value=quantity * avg_price
            ))
    
    return holdings
    