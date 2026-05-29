from fastapi import FastAPI
import uvicorn

from app.api.routes import router

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
        host="0.0.0.0",
        port=8000,
        reload=True
    )