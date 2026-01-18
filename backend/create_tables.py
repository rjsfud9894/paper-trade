from database import engine
from database import Base
from models import User
from models import Stock
from models import Trade

# 테이블 생성!
Base.metadata.create_all(bind=engine)

print("테이블 생성 완료!")
