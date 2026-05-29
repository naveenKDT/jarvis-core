from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import router
from app.core import settings

app = FastAPI(
    title="JARVIS CORE",
    version="1.0",
    docs_url="/docs" if settings.APP_RELOAD else None,
    redoc_url="/redoc" if settings.APP_RELOAD else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.JARVIS_CORS_ORIGINS,
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
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
    )
