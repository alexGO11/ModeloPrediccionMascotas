from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, InvalidTokenError

from config.settings_env import settings
from schema.user_schema import TokenData, User, UserOut
from model.user import users

from config.db_connection import engine
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# This function retrieves the current user from the token.
# It decodes the token and checks if the user exists in the database.
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    try:
        with engine.connect() as conn:
            query = select(users).where(users.c.username == token_data.username)
            result = conn.execute(query).mappings().fetchone()  # `mappings()` convierte a dict

            if result is None:
                raise credentials_exception

            return UserOut(
                username=result["username"],
                email=result["email"],
                full_name=result["full_name"]
            )
    except Exception as e:
        print(e)
        

# This function checks if the user is active or not.
# If the user is inactive, it raises an HTTPException with a 400 status code.
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
