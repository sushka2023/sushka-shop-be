from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'postgresql+psycopg2://user:password@server:5432/database'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    cloudinary_name: str = '_'
    cloudinary_api_key: str = '_'
    cloudinary_api_secret: str = '_'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
