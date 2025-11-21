from sqlalchemy import Column, Integer, String, Float, DateTime
from db_bk import Base
import datetime

class Part(Base):
    __tablename__ = "parts"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    photo = Column(String)
    
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    image_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)