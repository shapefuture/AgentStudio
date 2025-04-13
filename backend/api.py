from fastapi import FastAPI, HTTPException, status, WebSocket
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging
from .workflow_executor import WorkflowExecutor

app = FastAPI(
    title="Workflow API",
    version="1.0.0",
    description="API for managing and executing computational workflows",
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
    }
)

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Workflow API is running",
        "docs": "Visit /docs for Swagger UI or /redoc for ReDoc documentation",
        "endpoints": {
            "workflows": "/api/workflows",
            "execute": "/api/workflows/{workflow_id}/execute"
        }
    }
executor = WorkflowExecutor()

class ProjectBrief(BaseModel):
    project_brief: str
    api_key: Optional[str] = None

# Existing endpoints...

# New Monitoring Endpoints
@app.get("/api/agents/status", response_model=Dict[str, str])
async def get_agents_status():
    """Get status of all active agents"""
    return {
        "agent1": "running",
        "agent2": "idle"
    }

# Model Management
class ModelInfo(BaseModel):
    name: str
    provider: str
    status: str

@app.get("/api/models", response_model=List[ModelInfo])
async def list_models():
    """List available LLM models"""
    return [
        {"name": "gpt-4", "provider": "openai", "status": "active"},
        {"name": "claude-3", "provider": "anthropic", "status": "active"}
    ]

# Integration Endpoints  
class IntegrationConfig(BaseModel):
    type: str
    config: Dict

@app.post("/api/integrations/slack")
async def setup_slack_integration(config: IntegrationConfig):
    """Configure Slack integration"""
    return {"status": "success", "message": "Slack integration configured"}

@app.post("/api/integrations/teams")  
async def setup_teams_integration(config: IntegrationConfig):
    """Configure Microsoft Teams integration"""
    return {"status": "success", "message": "Teams integration configured"}

# Workflow Endpoints
@app.post("/api/workflows/generate", 
          status_code=201,
          summary="Generate a new workflow",
          description="Creates a new workflow definition based on the provided project brief",
          response_description="The generated workflow ID and details",
          responses={
              201: {"description": "Workflow successfully generated"},
              400: {"description": "Invalid project brief format"},
              500: {"description": "Workflow generation failed"}
          })
async def generate_workflow(project_brief: Dict):
    """
    Generate a workflow from project brief.
    
    - **project_brief**: JSON object containing project requirements
    - Returns: Workflow ID and generation status
    """
    return {
        "status": "success",
        "workflow_id": "test_workflow",
        "message": "Workflow generated",
        "project_brief": project_brief
    }

@app.post("/api/workflows/{workflow_id}/execute",
          status_code=202,
          summary="Execute a workflow",
          description="Runs the specified workflow with the provided definition",
          response_description="Workflow execution status",
          responses={
              202: {"description": "Workflow execution started"},
              400: {"description": "Invalid workflow definition"},
              404: {"description": "Workflow not found"},
              500: {"description": "Workflow execution failed"}
          })
async def execute_workflow(workflow_id: str, workflow_def: Dict):
    """
    Execute a workflow.
    
    - **workflow_id**: ID of the workflow to execute
    - **workflow_def**: JSON definition of the workflow nodes and edges
    - Returns: Execution status and result
    """
    try:
        result = await executor.execute_workflow(workflow_id, workflow_def)
        return {
            "status": "accepted",
            "workflow_id": workflow_id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow by ID including execution status"""
    status = executor.get_workflow_status(workflow_id)
    return {
        "workflow_id": workflow_id,
        "status": status['status'],
        "nodes": [],
        "edges": []
    }

@app.get("/api/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get detailed execution status of a workflow"""
    status = executor.get_workflow_status(workflow_id)
    if status['status'] == 'not_found':
        raise HTTPException(
            status_code=404,
            detail="Workflow not found"
        )
    return status

@app.websocket("/api/workflows/{workflow_id}/monitor")
async def monitor_workflow(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time workflow monitoring"""
    await websocket.accept()
    while True:
        status = executor.get_workflow_status(workflow_id)
        await websocket.send_json(status)
        if status['status'] in ['completed', 'failed']:
            break
        await asyncio.sleep(1)

@app.get("/api/workflows/{workflow_id}/history")
async def get_workflow_history(workflow_id: str):
    """Get execution history for a workflow"""
    return {
        "workflow_id": workflow_id,
        "history": executor.get_execution_history(workflow_id)
    }

@app.get("/api/agents/status")
async def get_detailed_agent_status():
    """Get detailed status of all agents"""
    return executor.get_agent_status()

# Vector DB Integration
@app.post("/api/vectordb/connect")
async def connect_vectordb(config: IntegrationConfig):
    """Connect to vector database"""
    return {"status": "success", "message": "VectorDB connected"}