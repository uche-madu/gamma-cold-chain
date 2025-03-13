from loguru import logger
from pydantic import EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mail_username: EmailStr
    mail_password: SecretStr
    mail_from: EmailStr
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_from_name: str
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True

    GROQ_API_KEY: SecretStr = Field(..., alias='GROQ_API_KEY')
     
    twilio_account_sid: SecretStr
    twilio_auth_token: SecretStr
    twilio_phone_number: str
    twilio_verified_phone_number: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        env_file_encoding="utf-8",
    )

settings = Settings() # type: ignore

logger.info(f"{Settings().model_dump()}") # type: ignore