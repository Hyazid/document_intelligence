from pydantic_settings import BaseSettings
from wrapt import lru_cache

class Settings(BaseSettings):
    database_url:str 
    lm_studio_url:str = "http://localhost:1234/v1"
    embedding_model:str = "nomic-embed-text-v1.5"
    llm_model:str='mistral-7b-instruct-v0.3'
    lm_studio_api_key: str = "lm-studio" 
    embed_dimensions: int = 768

    chunk_size: int = 512
    chunk_overlap: int = 64
    retrieval_top_k: int = 5
    #generation conservative for 6gb vram
    llm_temperature: float = 0.2
    llm_max_tokens: int = 512
    llm_context_window: int = 4096
    # langfuse settings
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    model_config = {
            "env_file": ".env",
            "extra": "ignore"       # ← silently ignores unknown .env keys
    }

    
    

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()



    