from sqlalchemy import select, insert
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from model.user import users 
from datetime import datetime, timedelta, timezone
from jose import jwt
from config.settings_env import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This function retrieves a user from the database by username.
# It takes a database session and username as input and returns a Row or None.
def get_user_by_username(db: Session, username: str) -> Row | None:
    query = select(users).where(users.c.username == username)
    result = db.execute(query).first()
    return result  # Este es un Row o None

# This function verifies the password by comparing the plain password with the hashed password.
# It takes the plain password and hashed password as input and returns True or False.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# This function authenticates a user by checking the username and password.
# It takes a database session, username, and password as input.
# If the user is found and the password is correct, it returns the user data.
def authenticate_user(db: Session, username: str, password: str):
    row = get_user_by_username(db, username)
    if not row:
        return None
    user = row._mapping  # para acceder como dict
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

# This function hashes the password using bcrypt.
# It takes a plain password as input and returns the hashed password.
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# This function creates a new user and inserts it the database.
# It takes a database session and user data as input.
def create_user(db: Session, user_data):
    existing_user = db.execute(
        select(users).where(users.c.username == user_data.username)
    ).first()

    if existing_user:
        return None  

    hashed_pw = get_password_hash(user_data.password)
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_pw,
        "disabled": False
    }

    db.execute(insert(users).values(**new_user))
    db.commit()
    return new_user

# This function creates a JWT token to grant access to the user.
# It takes a dictionary of data and an optional expiration time.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt