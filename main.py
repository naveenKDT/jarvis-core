from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import router
from app.core.settings import (
    JARVIS_CORS_ORIGINS,
    JARVIS_DEBUG,
    JARVIS_HOST,
    JARVIS_PORT,
)

app = FastAPI(
    title="JARVIS CORE",
    version="1.0",
    docs_url="/docs" if JARVIS_DEBUG else None,
    redoc_url="/redoc" if JARVIS_DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=JARVIS_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)


if __name__ == "__main__":

    print("")
    print("===================================")
    print("        JARVIS CORE ONLINE")
    print("===================================")
    print("")

    uvicorn.run(
        "main:app",
        host=JARVIS_HOST,
        port=JARVIS_PORT,
        reload=JARVIS_DEBUG,
    )
