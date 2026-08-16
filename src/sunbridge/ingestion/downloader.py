import logging
from pathlib import Path
import httpx
from sunbridge.config import settings, CACHE_DATA_DIR, DOCS_FALLBACK_DIR

logger = logging.getLogger(__name__)

def fetch_datasheet(url: str = None, force_redownload: bool = False) -> Path:
    """
    Downloads manufacturer PDF datasheet from URL or retrieves from local cache / fallback.
    Returns path to local PDF file.
    """
    if not url:
        url = settings.source1_url

    CACHE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    target_path = CACHE_DATA_DIR / "datasheet_sun_4_12k.pdf"
    fallback_path = DOCS_FALLBACK_DIR / "src1_task2.pdf"

    if target_path.exists() and not force_redownload:
        logger.info(f"Using cached datasheet at {target_path}")
        return target_path

    logger.info(f"Attempting to download datasheet from {url}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=15.0, follow_redirects=True, headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            with open(target_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Successfully downloaded datasheet to {target_path}")
            return target_path
    except Exception as e:
        logger.warning(f"Failed to download datasheet from URL ({e}). Checking local fallback...")
        if fallback_path.exists():
            logger.info(f"Using local fallback datasheet from {fallback_path}")
            # Copy or return fallback path
            with open(fallback_path, "rb") as src, open(target_path, "wb") as dst:
                dst.write(src.read())
            return target_path
        elif target_path.exists():
            logger.info(f"Using existing cached copy at {target_path}")
            return target_path
        else:
            raise RuntimeError(f"Could not retrieve datasheet from {url} and no local fallback found at {fallback_path}") from e
