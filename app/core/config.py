from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = Field(default="jd-fit-agent")
    app_description: str = Field(default="AI Agent for JD analysis, resume matching, fit scoring, and application strategy.")
    api_version: str = Field(default="0.1.0")

    app_env: str = Field(default="local")
    debug: bool = Field(default=True)

    api_v1_prefix: str = Field(default="/api/v1")

    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

