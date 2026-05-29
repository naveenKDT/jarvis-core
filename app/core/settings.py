import os

from dotenv import load_dotenv

load_dotenv()


# ── Security ────────────────────────────────────────────
JARVIS_API_KEY: str = os.getenv("JARVIS_API_KEY", "")

JARVIS_CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("JARVIS_CORS_ORIGINS", "").split(",")
    if origin.strip()
]

MAX_COMMAND_LENGTH: int = 2000

# ── Server ──────────────────────────────────────────────
APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
APP_RELOAD: bool = os.getenv("APP_RELOAD", "false").lower() == "true"

# ── Ollama / LLM ────────────────────────────────────────
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "300"))

# ── Generated output ────────────────────────────────────
GENERATED_SITES_DIR: str = os.getenv("GENERATED_SITES_DIR", "generated_sites")

# ── Logging ─────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
