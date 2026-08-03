from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    # MongoDB configuration
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017/financial",
        env="MONGO_URI"
    )
    MONGO_DB_NAME: str = Field(
        default="financial",
        env="MONGO_DB_NAME"
    )

    # Redis configuration (leave empty to disable cache — e.g. on Render without Redis)
    REDIS_URL: str = Field(
        default="",
        env="REDIS_URL"
    )

    # External API keys
    NEWS_API_KEY: str = Field(default="", env="NEWS_API_KEY")

    # ⭐ Added LLM API Keys (Groq + Gemini)
    GROQ_API_KEY: str = Field(default="", env="GROQ_API_KEY")
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")

    # Feature toggles
    YFINANCE_ENABLED: bool = Field(default=True, env="YFINANCE_ENABLED")

    # General configuration
    APP_NAME: str = "Financial Research Agent"
    ENV: str = Field(default="dev", env="ENV")

    # Optional LangChain tracing settings (for debugging/monitoring)
    langchain_tracing_v2: str = Field(default="", env="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field(default="", env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="", env="LANGCHAIN_PROJECT")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields in .env that aren't defined here
    )


# Global settings instance
settings = Settings()
