from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    email: str 
    username: str | None = None
    full_name: str | None = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

    model_config = {
        'from_attributes': True
    }