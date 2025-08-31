from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This function verifies the password by comparing the plain password with the hashed password.
# It takes the plain password and hashed password as input and returns True or False.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# This function returns the password hashed using bcrypt.
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
