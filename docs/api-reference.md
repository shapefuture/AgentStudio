# API Reference

## Workflows
- `POST /api/workflows/generate` - Create new workflow from project brief  
  - Status Code: 201 Created
  - Request Body: `{"project_brief": string}`  
  - Returns workflow ID

- `GET /api/workflows/{id}` - Get workflow status
  - Status Code: 200 OK
  - Returns workflow metadata and status

## Agents  
- `GET /api/agents/status` - Get agents monitoring
  - Status Code: 200 OK
  - Returns agent statuses

## Models
- `GET /api/models` - List available LLM models
  - Status Code: 200 OK  
  - Returns model metadata

## Deployment Info
- Production: Docker + Prometheus monitoring
- CI/CD: GitHub Actions pipeline