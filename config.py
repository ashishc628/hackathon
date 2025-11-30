# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "zk_loci")

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def has_openai_key(self) -> bool:
        return bool(self.OPENAI_API_KEY)

settings = Settings()
