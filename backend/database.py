from sqlalchemy import create_engine,Column,Integer,String,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

SQL_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQL_DATABASE_URL, connect_args = {'check_same_thread':False})
SessionLocal = sessionmaker(autocommit = False, autoflush=False,bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True,index=True)
    email = Column(String, unique=True, index=True,nullable=False)
    hashed_password = Column(String,nullable=False)
    name = Column(String)
    picture = Column(String)
    role = Column(String,default='user')
    created_at = Column(DateTime,default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
