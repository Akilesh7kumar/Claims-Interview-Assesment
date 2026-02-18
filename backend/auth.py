from datetime import datetime,timedelta,timezone
from typing import Annotated,Optional
from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError,jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db,User
from .schemas import Token,UserOut
from dotenv import load_dotenv
import os
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRY = 60*24 # 1 day
print(ALGORITHM)
pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(plain_password):
    return pwd_context.hash(plain_password)

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRY)
    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate':'Bearer'}
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email:str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return credentials_exception
    return UserOut.model_validate(user)

