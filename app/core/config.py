from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = Field(default="local")
    debug: bool = Field(default=True)

    app_name: str = Field(default="jd-fit-agent")
    app_description: str = Field(default="AI Agent for JD analysis, resume matching, fit scoring, and application strategy.")
    api_version: str = Field(default="0.1.0")

    api_v1_prefix: str = Field(default="/api/v1")

    database_url: str

    resume_chunk_size: int = 800
    resume_chunk_overlap: int = 120

    #OpenAI
    openai_api_key: str
    embedding_modeL: str = Field(default="text-embedding-3-small")
    embedding_dimensions: int = Field(default=1536)
    llm_model: str = Field(default="gpt-4o-mini")

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

