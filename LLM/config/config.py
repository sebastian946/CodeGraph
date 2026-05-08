
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    REDIS_URL: str
    ENVIRONMENT: str
    LOG_LEVEL: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")

    def _get_env_variable(self, var_name: str) -> str:
        settings = Settings() # type: ignore[call-arg]
        settings_dict = settings.model_dump()
        variable = settings_dict.get(var_name)
        if not variable:
            raise ValueError(f"Environment variable '{var_name}' is required but not set.")
        return variable