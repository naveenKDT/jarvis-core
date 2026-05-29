from fastapi import APIRouter
from pydantic import BaseModel

from app.core.brain import JarvisBrain

router = APIRouter()

brain = JarvisBrain()


class CommandRequest(BaseModel):
    command: str


@router.get("/")
async def root():

    return {
        "name": "JARVIS CORE",
        "status": "online"
    }


@router.post("/command")
async def process_command(request: CommandRequest):

    result = await brain.think(request.command)

    return result