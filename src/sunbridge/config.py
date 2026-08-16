import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CACHE_DATA_DIR = DATA_DIR / "cache"
INPUT_DATA_DIR = DATA_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
DOCS_FALLBACK_DIR = BASE_DIR / "Docs"

class Settings(BaseModel):
    llm_base_url: str = Field(default_factory=lambda: os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    llm_api_key: str = Field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    llm_temperature: float = Field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.0")))

    source1_url: str = "https://www.deyeinverter.com/deyeinverter/2023/10/07/datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf"
    
    def ensure_directories(self):
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        INPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
