from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    # You can fill .env file or write directly in here
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    PROJECT_NAME: str = "LztMarketPriceScript"
    
    MARKET_API_URL: str = "https://prod-api.lzt.market/"
    MARKET_API_TOKEN: str = ""
    
    TG_BOT_API_TOKEN: str = ""
    
    PERCENT_OF_SELLER: int = 20



settings = Settings()