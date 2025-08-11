from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from schema.user_schema import UserCreate
from auth.auth_service import create_user
from config.db_connection import SessionLocal

from schema.user_schema import Token, User, UserOut
from auth.auth_service import authenticate_user, create_access_token
from auth.dependencies import get_current_user

auth_routes = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to login and returns a token
@auth_routes.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print("iniciando autenticación, usuario:", form_data.username)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        print("usuario no encontrado o contraseña incorrecta")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print("usuario autenticado:", user.username)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_routes.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Endpoint to register a new user 
@auth_routes.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    created_user = create_user(db, user)
    if not created_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    return created_user