from fastapi import FastAPI
import uvicorn

from app.api.routes import router
from app.core import settings

app = FastAPI(
    title="JARVIS CORE",
    version="1.0"
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
        reload=settings.APP_RELOAD
    )
