"""Application configuration."""
import os
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
ENV_FILE = PROJECT_ROOT / ".env"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(ENV_FILE)

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATA_DIR / 'secagentx.db'}")

_llm_type = os.environ.get("LLM_TYPE", "deepseek")
_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
if not _api_key and _llm_type != "local":
    _llm_type = "local"

DEFAULT_LLM_CONFIG: Dict[str, Any] = {
    "type": _llm_type,
    "api_key": _api_key,
    "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model_name": os.environ.get("LLM_MODEL", "deepseek-v4-flash"),
}

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

APP_NAME = "SecAgentX"
APP_VERSION = "0.1.0"
