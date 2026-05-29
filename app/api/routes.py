from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, field_validator

from app.core.brain import JarvisBrain
from app.core.settings import JARVIS_API_KEY, MAX_COMMAND_LENGTH

router = APIRouter()

brain = JarvisBrain()


def verify_api_key(
    authorization: str = Header(default=""),
) -> None:
    if not JARVIS_API_KEY:
        return

    expected = f"Bearer {JARVIS_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class CommandRequest(BaseModel):
    command: str

    @field_validator("command")
    @classmethod
    def validate_command_length(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("command must not be empty")
        if len(v) > MAX_COMMAND_LENGTH:
            raise ValueError(
                f"command must not exceed {MAX_COMMAND_LENGTH} characters"
            )
        return v.strip()


@router.get("/")
async def root():

    return {
        "name": "JARVIS CORE",
        "status": "online"
    }


@router.post("/command")
async def process_command(
    request: CommandRequest,
    _: None = Depends(verify_api_key),
):

    result = await brain.think(request.command)

    return result
