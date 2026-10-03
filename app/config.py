from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    database_url:str="postgresql+asyncpg://postgres:postgres@localhost:5432/sim"
    redis_url:str="redis://localhost:6379/0"
    api_key:str="change-me"
    max_parallel_users:int=50
    environment:str="local"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
