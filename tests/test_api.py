from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "JARVIS CORE"
    assert data["status"] == "online"


def test_command():
    response = client.post(
        "/command",
        json={"command": "hello"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "jarvis" in data["response"].lower()
