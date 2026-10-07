from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/competitor_pulse"
    cors_origins: list[str] = ["http://localhost:5173"]
    app_url: str = "http://localhost:5173"

    # When true the API is read-only: browse seeded runs, no writes or new runs.
    demo_mode: bool = False

    # Agent
    agent_model: str = "claude-opus-5-5"
    agent_effort: str = "medium"
    agent_max_turns: int = 40
    agent_max_budget_usd: float = 2.0

    # Worker
    schedule_cron: str = "0 8 * * MON"
    worker_poll_seconds: float = 3.0
    crawl_concurrency: int = 4
    crawl_timeout_ms: int = 30_000

    # Notifications
    smtp_host: str = ""
    smtp_port: int = 1025
    smtp_from: str = "competitor-pulse@localhost"


settings = Settings()
