import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_file)

db_path = os.path.join(BASE_DIR, "data", "pipeline.db").replace('\\', '/')

class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")

settings = Settings()
