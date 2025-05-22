from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from schema.user_schema import Token, User
from auth.auth_service import authenticate_user, create_access_token
from auth.dependencies import get_current_user

auth_routes = APIRouter()

@auth_routes.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_routes.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user