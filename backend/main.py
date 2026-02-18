from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import get_db, User
from .schemas import UserCreate, UserOut, Token
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost:8501","http://127.0.0.1:8501"
    ],
    allow_headers=["*"],
    allow_methods = ["*"],
    allow_credentials = True
)

@app.post('/register',response_model=UserOut)
def register_user(user:UserCreate,db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400,detail='User ALready Registered')
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email = user.email,
        hashed_password = hashed_password,
        name = user.email.split('@')[0].title()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut.model_validate(new_user)

@app.get('/users/me',response_model=UserOut)
def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@app.post('/login',response_model=Token)
def login(form_data:OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail ="Incorrect credentails",
            headers={'WWW-Authenticate':'Bearer'},
        )
    access_token = create_access_token(data = {'sub':user.email})
    return {'access_token': access_token,'token_type':'bearer' }