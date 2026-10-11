from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/competitor_pulse"
    cors_origins: list[str] = ["http://localhost:5173"]
    app_url: str = "http://localhost:5173"

    # When true the API is read-only: browse seeded runs, no writes or new runs.
    demo_mode: bool = False

    # Pre-filled by "Try the sample company" on first run; docker-compose points it at demo-sites.
    sample_company_url: str = ""

    # Agent
    anthropic_api_key: str = ""
    # One model per agent. The analyst and company discovery need judgment; page discovery picks
    # URLs from links it has already crawled. The comparison behind this is in docs/evals.md.
    analyst_model: str = "claude-opus-5-5"
    company_discovery_model: str = "claude-opus-5-5"
    page_discovery_model: str = "claude-haiku-5-5"
    agent_effort: str = "medium"
    agent_max_turns: int = 40
    agent_max_budget_usd: float = 2.0
    # Caps keep discovery focused and bound the cost of every later check.
    discovery_max_competitors: int = 3
    discovery_max_pages: int = 5

    # Worker
    schedule_cron: str = "0 8 * * MON"
    worker_poll_seconds: float = 3.0
    # Runs one worker executes at once (e.g. page discovery for each new competitor).
    worker_concurrency: int = 4
    crawl_concurrency: int = 4
    crawl_timeout_ms: int = 30_000

    # Notifications
    smtp_host: str = ""
    smtp_port: int = 1025
    smtp_from: str = "competitor-pulse@localhost"


settings = Settings()
