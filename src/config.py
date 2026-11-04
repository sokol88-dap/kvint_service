from pydantic import Field, MongoDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    mongo_url: MongoDsn = "mongodb://localhost:27017"
    rabbitmq_host: str = "localhost"
    rabbitmq_user: str = Field(min_length=1)
    rabbitmq_password: SecretStr = Field(min_length=1)
