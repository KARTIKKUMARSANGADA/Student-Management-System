from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ✅ Test root endpoint
def test_welcome():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome TO Student Management System"
    }


# ✅ Test metrics endpoint
def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

