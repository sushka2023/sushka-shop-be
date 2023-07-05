from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'postgresql+psycopg2://user:password@server:5432/database'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    cloudinary_name: str = '_'
    cloudinary_api_key: str = '_'
    cloudinary_api_secret: str = '_'
    mail_username: str = 'username'
    mail_password: str = 'password'
    mail_from: str = 'from'
    mail_port: str = 'port'
    mail_server: str = 'server'
    mail_from_name: str = 'mail_name'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
