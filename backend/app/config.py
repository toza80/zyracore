from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://zyra:changeme@postgres:5432/zyraworks"
    redis_url: str = "redis://redis:6379/0"

    llm_provider: str = "deepseek"

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"

    telegram_bot_token: str = ""
    telegram_allowed_user_ids: str = ""  # csv de ids, ej: "12345,67890"

    require_approval_for_actions: bool = True

    @property
    def allowed_telegram_ids(self) -> set[int]:
        return {
            int(x.strip())
            for x in self.telegram_allowed_user_ids.split(",")
            if x.strip().isdigit()
        }


settings = Settings()
