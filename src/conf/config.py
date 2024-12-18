from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    @property
    def sqlalchemy_database_url(self):
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@localhost:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
