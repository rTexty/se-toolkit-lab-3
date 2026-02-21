import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.outcome import Outcome
from app.database import get_session

async def override_get_session():
    yield AsyncMock()

app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

@pytest.fixture
def mock_db():
    with patch("app.routers.outcomes.create_outcome", new_callable=AsyncMock) as mock_create, \
         patch("app.routers.outcomes.read_outcomes", new_callable=AsyncMock) as mock_read_all, \
         patch("app.routers.outcomes.read_outcome", new_callable=AsyncMock) as mock_read_one:
        yield mock_create, mock_read_all, mock_read_one

def test_create_outcome(mock_db):
    mock_create, _, _ = mock_db
    mock_create.return_value = Outcome(id=1, learner_id=1, item_id=1, status="passed", created_at="2025-01-01T00:00:00")
    
    response = client.post(
        "/outcomes/",
        json={"learner_id": 1, "item_id": 1, "status": "passed"},
        headers={"Authorization": "Bearer my-secret-api-key"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["learner_id"] == 1
    assert data["item_id"] == 1
    assert data["status"] == "passed"
    assert "id" in data

def test_get_outcomes(mock_db):
    _, mock_read_all, _ = mock_db
    mock_read_all.return_value = [Outcome(id=1, learner_id=1, item_id=1, status="passed", created_at="2025-01-01T00:00:00")]
    
    response = client.get("/outcomes/", headers={"Authorization": "Bearer my-secret-api-key"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "passed"

def test_get_outcome_by_id(mock_db):
    _, _, mock_read_one = mock_db
    mock_read_one.return_value = Outcome(id=1, learner_id=1, item_id=1, status="passed", created_at="2025-01-01T00:00:00")
    
    response = client.get("/outcomes/1", headers={"Authorization": "Bearer my-secret-api-key"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "passed"

def test_get_nonexistent_outcome(mock_db):
    _, _, mock_read_one = mock_db
    mock_read_one.return_value = None
    
    response = client.get("/outcomes/9999", headers={"Authorization": "Bearer my-secret-api-key"})
    assert response.status_code == 404
