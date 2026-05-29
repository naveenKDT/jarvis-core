from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect

from app.brain.orchestrator import Orchestrator
from app.brain.task_manager import TaskManager
from app.core import settings
from app.core.models import (
    CalendarEventCreate,
    CommandRequest,
    CommandResponse,
    DeviceCommand,
    HealthLogCreate,
    ReminderCreate,
)
from app.memory import long_term
from app.websocket.manager import ws_manager

router = APIRouter()

orchestrator = Orchestrator()
task_manager = TaskManager()


def verify_api_key(authorization: str = Header(default="")) -> None:
    if not settings.JARVIS_API_KEY:
        return
    expected = f"Bearer {settings.JARVIS_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ── Core ─────────────────────────────────────────────────

@router.get("/")
async def root():
    return {
        "name": "JARVIS CORE",
        "status": "online",
        "version": "2.0",
        "agents": ["assistant", "coding", "device", "file", "website"],
    }


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.post("/command", response_model=CommandResponse)
async def process_command(
    request: CommandRequest,
    _: None = Depends(verify_api_key),
):
    result = await orchestrator.execute(request.command)
    return CommandResponse(
        success=result.get("success", True),
        response=result.get("response", ""),
        agent=result.get("agent"),
        data=result.get("data"),
    )


# ── Reminders ────────────────────────────────────────────

@router.post("/reminders")
async def create_reminder(
    reminder: ReminderCreate,
    _: None = Depends(verify_api_key),
):
    reminder_id = long_term.create_reminder(
        title=reminder.title,
        description=reminder.description,
        due_at=reminder.due_at,
        priority=reminder.priority.value,
        recurring=reminder.recurring,
    )
    return {"id": reminder_id, "message": "Reminder created"}


@router.get("/reminders")
async def list_reminders(_: None = Depends(verify_api_key)):
    return {"reminders": long_term.get_reminders()}


@router.get("/reminders/due")
async def get_due_reminders(_: None = Depends(verify_api_key)):
    return {"reminders": long_term.get_due_reminders()}


@router.post("/reminders/{reminder_id}/complete")
async def complete_reminder(
    reminder_id: int,
    _: None = Depends(verify_api_key),
):
    long_term.complete_reminder(reminder_id)
    return {"message": f"Reminder {reminder_id} completed"}


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: int,
    _: None = Depends(verify_api_key),
):
    long_term.delete_reminder(reminder_id)
    return {"message": f"Reminder {reminder_id} deleted"}


# ── Calendar ─────────────────────────────────────────────

@router.post("/calendar")
async def create_calendar_event(
    event: CalendarEventCreate,
    _: None = Depends(verify_api_key),
):
    event_id = long_term.create_calendar_event(
        title=event.title,
        start_at=event.start_at,
        end_at=event.end_at,
        description=event.description,
        location=event.location,
    )
    return {"id": event_id, "message": "Calendar event created"}


@router.get("/calendar")
async def list_calendar_events(_: None = Depends(verify_api_key)):
    return {"events": long_term.get_calendar_events()}


@router.delete("/calendar/{event_id}")
async def delete_calendar_event(
    event_id: int,
    _: None = Depends(verify_api_key),
):
    long_term.delete_calendar_event(event_id)
    return {"message": f"Calendar event {event_id} deleted"}


# ── Health ───────────────────────────────────────────────

@router.post("/health/log")
async def log_health(
    entry: HealthLogCreate,
    _: None = Depends(verify_api_key),
):
    log_id = long_term.log_health(
        category=entry.category,
        value=entry.value,
        notes=entry.notes,
    )
    return {"id": log_id, "message": "Health data logged"}


@router.get("/health/logs")
async def get_health_logs(
    category: str | None = None,
    _: None = Depends(verify_api_key),
):
    return {"logs": long_term.get_health_logs(category=category)}


@router.get("/health/summary")
async def get_health_summary(_: None = Depends(verify_api_key)):
    return {"summary": long_term.get_health_summary()}


# ── Device ───────────────────────────────────────────────

@router.post("/device/command")
async def device_command(
    cmd: DeviceCommand,
    _: None = Depends(verify_api_key),
):
    result = await orchestrator.agents["device"].execute(
        f"{cmd.action} {cmd.device_type.value}"
    )
    return result


@router.get("/device/tv/status")
async def tv_status(_: None = Depends(verify_api_key)):
    tv = orchestrator.agents["device"].tv
    power = tv.get_power_status()
    volume = tv.get_volume()
    return {"power": power, "volume": volume}


@router.get("/device/tv/discover")
async def discover_tv(_: None = Depends(verify_api_key)):
    from app.devices.tv.sony_bravia import SonyBraviaTV
    devices = SonyBraviaTV.discover()
    return {"devices": devices}


# ── Tasks ────────────────────────────────────────────────

@router.get("/tasks")
async def list_tasks(
    status: str | None = None,
    _: None = Depends(verify_api_key),
):
    return {"tasks": long_term.get_tasks(status=status)}


# ── Conversations ────────────────────────────────────────

@router.get("/conversations")
async def list_conversations(
    limit: int = 50,
    _: None = Depends(verify_api_key),
):
    return {"conversations": long_term.get_conversations(limit=limit)}


# ── System ───────────────────────────────────────────────

@router.get("/system/status")
async def system_status(_: None = Depends(verify_api_key)):
    return {
        "status": "online",
        "agents": {
            name: {"status": "ready"}
            for name in orchestrator.agents
        },
        "voice_enabled": settings.VOICE_ENABLED,
        "llm_model": settings.OLLAMA_MODEL,
        "llm_url": settings.OLLAMA_BASE_URL,
    }


# ── WebSocket ────────────────────────────────────────────

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command", "")
            if command:
                result = await orchestrator.execute(command)
                await websocket.send_json(result)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
