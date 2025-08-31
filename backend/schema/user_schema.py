from pydantic import BaseModel, EmailStr

# Represents a token used for authentication, including the token string and its type
class Token(BaseModel):
    access_token: str
    token_type: str

# Represents the data contained in a token, such as the username
class TokenData(BaseModel):
    username: str | None = None

# Represents a user with basic information such as email, username, and full name
class User(BaseModel):
    email: str 
    username: str | None = None
    full_name: str | None = None

# Extends the User class to include the hashed password for database storage
class UserInDB(User):
    hashed_password: str

# Represents the data required to create a new user, including username, email, and password
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str

# Represents the data returned when querying user information, excluding sensitive fields
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

    model_config = {
        'from_attributes': True
    }