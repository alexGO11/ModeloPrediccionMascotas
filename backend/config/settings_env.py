from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define a Settings class to manage application configuration
class Settings(BaseSettings):
    # Database configuration
    db_name: str = Field(validation_alias='DB_NAME')
    db_user: str = Field(validation_alias='DB_USER')
    db_pass: str = Field(validation_alias='DB_PASSWORD')
    db_host: str = Field(validation_alias='DB_HOST')
    db_dialect: str = Field(validation_alias='DB_DIALECT')
    mysql_user :str = Field(validation_alias='MYSQL_USER')
    mysql_pass :str = Field(validation_alias='MYSQL_PASSWORD')

    # Security configuration
    secret_key: str = Field(validation_alias='SECRET_KEY')
    algorithm: str = Field(validation_alias='ALGORITHM')
    token_expire: int = Field(validation_alias='ACCESS_TOKEN_EXPIRE_MINUTES')

# Instantiate the Settings class to access configuration values
settings = Settings()