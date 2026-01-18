from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from database import Base


class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
