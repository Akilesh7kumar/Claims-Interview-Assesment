from pydantic import BaseModel, EmailStr, Field,ConfigDict

class UserBase(BaseModel):
    email : EmailStr

class UserCreate(UserBase):
    password : str = Field(..., min_length=5)

class UserOut(UserBase):
    id : int
    name : str | None = None
    picture : str | None = None
    role : str

    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token:str
    token_type : str = 'bearer'