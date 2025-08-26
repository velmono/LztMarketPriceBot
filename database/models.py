from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import Integer, String, BigInteger

Base = declarative_base()

class Users(Base):
    __tablename__ = "Users"
    
    id = mapped_column(Integer, primary_key = True)
    user_id = mapped_column(BigInteger, index = True)
    share_percent = mapped_column(Integer)