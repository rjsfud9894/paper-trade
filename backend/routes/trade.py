from fastapi import APIRouter
from pydantic import BaseModel

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
