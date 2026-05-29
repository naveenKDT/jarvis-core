import os


JARVIS_API_KEY: str = os.getenv("JARVIS_API_KEY", "")

JARVIS_HOST: str = os.getenv("JARVIS_HOST", "127.0.0.1")

JARVIS_PORT: int = int(os.getenv("JARVIS_PORT", "8000"))

JARVIS_DEBUG: bool = os.getenv("JARVIS_DEBUG", "false").lower() == "true"

JARVIS_CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("JARVIS_CORS_ORIGINS", "").split(",")
    if origin.strip()
]

MAX_COMMAND_LENGTH: int = 2000
