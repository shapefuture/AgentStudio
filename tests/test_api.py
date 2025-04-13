from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api import app
import json

client = TestClient(app)

def test_workflow_status():
    response = client.get("/api/workflows/test_id")
    assert response.status_code == 200
    assert response.json()["workflow_id"] == "test_id"
    
def test_project_brief_model():
    response = client.post(
        "/api/workflows/generate",
        json={"project_brief": "Test project"}
    )
    assert response.status_code == 201
    assert "workflow_id" in response.json()
    
def test_agents_status():
    response = client.get("/api/agents/status")
    assert response.status_code == 200
    assert "agent1" in response.json()

def test_list_models():
    response = client.get("/api/models")
    assert response.status_code == 200
    assert len(response.json()) > 0

if __name__ == "__main__":
    import unittest
    unittest.main()