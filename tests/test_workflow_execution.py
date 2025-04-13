from fastapi.testclient import TestClient
from backend.api import app
import pytest

client = TestClient(app)

def test_execute_workflow():
    test_workflow = {
        "nodes": [
            {"id": "node1", "function": "lambda x: x + 1"},
            {"id": "node2", "function": "lambda x: x * 2"}
        ],
        "edges": [
            {"source": "node1", "target": "node2"}
        ],
        "entry_point": "node1",
        "input": 5  # Simplified input format
    }
    
    # First generate workflow
    gen_response = client.post(
        "/api/workflows/generate",
        json={"project_brief": "test workflow"}
    )
    workflow_id = gen_response.json()["workflow_id"]
    
    # Then execute it
    exec_response = client.post(
        f"/api/workflows/{workflow_id}/execute",
        json=test_workflow
    )
    assert exec_response.status_code == 202
    
    # Check status
    status_response = client.get(f"/api/workflows/{workflow_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] in ["running", "completed"]

def test_get_workflow_status_not_found():
    response = client.get("/api/workflows/nonexistent/status")
    assert response.status_code == 404
    assert response.json()["detail"] == "Workflow not found"
