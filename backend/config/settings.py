from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    db_name: str = Field(validation_alias='DB_NAME')
    db_user: str = Field(validation_alias='DB_USER')
    db_pass: str = Field(validation_alias='DB_PASSWORD')
    db_host: str = Field(validation_alias='DB_HOST')
    db_dialect: str = Field(validation_alias='DB_DIALECT')

    secret_key: str = Field(validation_alias='SECRET_KEY')
    algorithm: str = Field(validation_alias='ALGORITHM')
    token_expire: int = Field(validation_alias='ACCESS_TOKEN_EXPIRE_MINUTES')