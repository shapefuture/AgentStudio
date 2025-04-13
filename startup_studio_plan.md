# Plan for Autonomous Startup Studio

**Core Philosophy:** Build iteratively, focusing on delivering a functional end-to-end flow early and then enhancing components. Emphasize testing at each stage.

**Technology Stack Summary:** PraisonAI (Agents), LangGraph (Workflow Execution), FastAPI (API), React Flow (Visual UI), Supabase (DB/Auth), Docker, Vercel/Render, GitHub Actions.

---

## Phase 1: Foundation - Core Workflow Engine & Basic Execution

*   **Goal:** Establish the minimum viable backend pipeline: receive input, generate a *simple* workflow plan, execute it using placeholder agents, and log the process. Prove the core PraisonAI/LangGraph integration works.
*   **Steps:**
    1.  **Environment Setup:** Initialize project structure, install PraisonAI, LangGraph, FastAPI, basic dependencies (`requirements.txt`). Set up `.env` handling.
    2.  **Core Agent Templates (YAML):** Define 2-3 *basic* agent roles in PraisonAI YAML format (e.g., `SimplePlanner`, `TaskExecutorPlaceholder`, `DataLogger`). Focus on structure, not complex logic yet.
    3.  **Basic `WorkflowPlanner` Agent:** Implement a PraisonAI agent (`SimplePlanner`) that takes a text brief and uses a basic LLM call (via OpenRouter tool) to output a *fixed-structure or very simple sequential* workflow definition (JSON format suitable for LangGraph).
    4.  **LangGraph Integration:** Implement a LangGraph graph that can parse the simple workflow JSON generated in step 3. Define nodes that trigger corresponding PraisonAI agents (initially, the `TaskExecutorPlaceholder` which just logs its execution).
    5.  **Basic Error Handling (LangGraph):** Implement rudimentary error catching within the LangGraph execution flow (e.g., log failures, stop the graph).
    6.  **Tool Interface Definition:** Define the standard way tools will be created (`BaseTool` inheritance?) and registered/made available to PraisonAI agents. Implement one *very simple* tool (e.g., `LogMessageTool`).
    7.  **Minimal FastAPI Endpoint:** Create a single POST endpoint that accepts a text brief, triggers the `SimplePlanner` agent, receives the JSON workflow, initiates the LangGraph execution, and returns a basic status (e.g., "Workflow Started", "Workflow Completed/Failed").
    8.  **Basic Logging:** Implement simple logging throughout the FastAPI and agent execution process.
    9.  **Unit & Integration Testing:** Write unit tests for the planner's output parsing and LangGraph node functions. Write basic integration tests for the FastAPI endpoint triggering the whole sequence.

*   **Outcome:** A backend system that can take a text prompt, generate a trivial workflow, execute placeholder agents via LangGraph, and log the result. No UI, no real tools, no persistence yet.

---

## Phase 2: Visual Interface & Enhanced Workflow

*   **Goal:** Introduce the visual workflow editor, enable dynamic workflow generation based on the brief, allow UI modification of the plan *before* execution, and add basic persistence.
*   **Steps:**
    1.  **React Frontend Setup & Basic Visualization:**
        *   Create a new directory `frontend/`.
        *   Initialize a React project inside `frontend/` (e.g., using Vite: `npm create vite@latest frontend -- --template react`).
        *   Install `react-flow-renderer`: `cd frontend && npm install react-flow-renderer`.
        *   Develop a core `WorkflowEditor` component.
        *   Implement a basic API call (using `fetch` or `axios`) within `WorkflowEditor` to fetch workflow data from a new backend endpoint (to be created in Step 3).
        *   Use `react-flow-renderer` to display the fetched workflow nodes and edges on a canvas. Apply basic styling.
    2.  **UI Workflow Modification:**
        *   Add UI elements (e.g., a sidebar) listing available agent templates (like `market_analyst`, `basic_planner`).
        *   Implement drag-and-drop or button clicks to add new agent nodes to the canvas.
        *   Enable users to draw edges between nodes to define execution flow.
        *   Create a properties panel that appears when a node is selected, allowing users to edit task details or agent parameters.
        *   Implement node/edge deletion functionality.
        *   Manage the workflow state (nodes, edges, parameters) within the React component.
        *   Add a "Save" button that triggers an API call to send the updated workflow JSON to the backend (Step 3).
    3.  **Backend API Extension for UI & Workflow Management:**
        *   In `api.py`, add new FastAPI endpoints:
            *   `GET /api/workflows/{workflow_id}`: To retrieve a specific workflow JSON.
            *   `PUT /api/workflows/{workflow_id}`: To update a workflow JSON from the UI.
            *   `POST /api/workflows/{workflow_id}/execute`: To trigger the `LangGraphExecutor` for a saved workflow.
            *   (Optional) `GET /api/workflows`: To list available workflows.
        *   Modify the existing `POST /create_startup` endpoint:
            *   It should now call the `WorkflowPlanner`.
            *   Save the generated workflow JSON using a unique ID (e.g., to `workflows/{uuid}.json`).
            *   Return the `workflow_id` to the caller.
        *   Implement simple file-based storage in a `workflows/` directory for now. Each workflow is saved as a separate JSON file named by its ID.
    4.  **Enhance `WorkflowPlanner` for Complexity:**
        *   Refactor `praisonai/workflow_planner.py`.
        *   Update the `plan_workflow` method to generate JSON structures that LangGraph can interpret for:
            *   **Parallel Execution:** Identify tasks in the brief that can run concurrently and structure the `nodes` and `next` properties accordingly.
            *   **Conditional Paths:** Introduce nodes that represent decision points, potentially using a dedicated 'decision' agent or specific output parsing, leading to different `next` nodes based on conditions.
        *   Ensure the output JSON remains compatible with both LangGraph execution and `react-flow-renderer` visualization.
    5.  **LangGraph Enhancement:** Update the LangGraph executor to handle the more complex JSON structures (conditionals, parallel branches if supported).
    6.  **Integration Testing:** Test the full loop: UI loads workflow -> User modifies -> Saves via API -> Triggers execution -> LangGraph runs modified plan.

*   **Outcome:** A system with a visual UI to view and modify dynamically generated (but still simple) workflows before execution. Basic persistence is in place.

*   **Phase 2 Interaction Diagram:**
    ```mermaid
    sequenceDiagram
        participant FE as Frontend UI (React Flow)
        participant BE as Backend API (FastAPI)
        participant WP as WorkflowPlanner
        participant LE as LangGraphExecutor
        participant Store as Workflow Storage (JSON Files)

        alt Load Existing Workflow
            FE->>+BE: GET /api/workflows/{id}
            BE->>+Store: Read workflows/{id}.json
            Store-->>-BE: Workflow JSON
            BE-->>-FE: Workflow JSON
            Note over FE: Render workflow in React Flow
        end

        alt Modify and Save Workflow
            Note over FE: User modifies workflow visually
            FE->>+BE: PUT /api/workflows/{id} (Updated JSON)
            BE->>+Store: Write workflows/{id}.json
            Store-->>-BE: Success/Failure
            BE-->>-FE: Save Confirmation
        end

        alt Execute Workflow
            FE->>+BE: POST /api/workflows/{id}/execute
            BE->>+Store: Read workflows/{id}.json
            Store-->>-BE: Workflow JSON
            BE->>+LE: execute_workflow(workflow_json)
            Note over LE: Executes agents sequentially/parallelly based on JSON
            LE-->>BE: Status Update (Async)
            BE-->>-FE: Execution Status (e.g., "Started")
        end

        alt Create New Workflow (Initial Planning)
             User/Client->>+BE: POST /create_startup (brief)
             BE->>+WP: plan_workflow(brief)
             WP-->>BE: Generated Workflow JSON (potentially complex)
             BE->>+Store: Write workflows/{new_id}.json
             Store-->>-BE: Success, returns new_id
             BE-->>-User/Client: { workflow_id: new_id }
        end
    ```

---

## Phase 3: Tool Integration & Production Readiness

*   **Goal:** Integrate real-world tools, establish robust persistence, implement security, and deploy the application. Make the system capable of executing meaningful, multi-step workflows.

## Phase 4: Real-time Monitoring & Analytics

*   **Goal:** Implement comprehensive real-time monitoring and analytics for agent workflows
*   **Components:**
    1. **Execution Monitoring**
        - Real-time event handling via Chainlit interface
        - SQLite database for persistent state tracking
        - Conversation/item completion handlers
        - Error tracking and recovery flows
    2. **Performance Analytics**
        - Step-by-step execution logging
        - Workflow duration metrics
        - Success/failure rates per agent type
    3. **Visual Interface**
        - React Flow visualization of active workflows
        - Real-time status updates
        - Execution history review
    4. **Alerting System**
        - Threshold-based notifications
        - Error condition detection
        - Performance degradation alerts

## Phase 5: Results Analysis & Optimization

*   **Goal:** Analyze execution results and optimize agent performance
*   **Components:**
    1. **Result Aggregation**
        - Structured data collection from all workflow steps
        - Artifact versioning and comparison
    2. **Performance Analysis**
        - Agent response time metrics
        - Tool usage patterns
        - Error correlation analysis
    3. **Optimization Feedback Loop**
        - Automated agent configuration tuning
        - Workflow restructuring suggestions
        - Tool selection recommendations
*   **Steps:**
    1. **Data Collection Pipeline**
        - Implement structured logging for all workflow steps
        - Create data models for execution metrics
        - Set up automated data aggregation
    2. **Analytics Dashboard**
        - Build visualization components for key metrics
        - Implement filtering and drill-down capabilities
        - Set up scheduled reporting
    3. **Optimization Engine**
        - Develop configuration tuning algorithms
        - Implement A/B testing framework
        - Create feedback mechanisms to agents
    4. **Continuous Improvement Pipeline**
        - Set up automated performance benchmarking
        - Implement agent versioning and rollback
        - Create documentation generation for optimized workflows
    5. **Feedback Integration**
        - Develop user feedback collection system
        - Implement automated issue categorization
        - Create prioritization algorithms for improvements
    8.  **CI/CD Pipeline (GitHub Actions):** Set up workflows for automated testing, building Docker images, and deploying to staging/production environments on push/merge.
    9.  **Deployment Configuration (Vercel/Render):** Configure deployment services (e.g., Vercel for React frontend, Render for FastAPI backend + Supabase instance).
    10. **Basic Monitoring:** Integrate basic health checks. Set up logging aggregation (e.g., using Render's built-in logging or a simple ELK stack setup). Consider adding basic Prometheus metrics for API usage/performance.
    11. **End-to-End Testing:** Create test scripts that simulate a full project lifecycle: submitting a brief, generating a plan, executing a multi-step workflow with real tools, and verifying results in Supabase.

*   **Outcome:** A deployed, secure, V1 application capable of running meaningful automated workflows with real tools, visual oversight, and persistent state tracking. Ready for initial internal use or closed beta.

---

## Conceptual Flow Diagram:

```mermaid
graph TD
    A[Client Input: Business Idea Brief] --> B(FastAPI Endpoint);
    B --> C{WorkflowPlanner Agent (PraisonAI)};
    C -- Generates --> D[Workflow Definition (JSON)];
    D -- Stored/Retrieved --> E(Supabase DB);
    D --> F{Internal UI (React Flow)};
    F -- Visualizes/Modifies --> D;
    F -- Triggers Execution --> G(FastAPI Endpoint);
    G -- Loads Definition --> E;
    G -- Initiates --> H{LangGraph Executor};
    H -- Parses --> D;
    H -- Executes Step-by-Step --> I(PraisonAI Agent Execution);
    I -- Uses --> J[Agent Templates (YAML)];
    I -- Uses --> K[External Tools/APIs];
    I -- Reports Status/Results --> H;
    H -- Updates State --> E;
    H -- Produces --> L[Launched Product / PMF Validation Data];

    subgraph "Phase 1: Foundation"
        C; H; I; J; B; G;
    end

    subgraph "Phase 2: Visual UI & Dynamic Planning"
        F; E; D;
        style C fill:#f9d,stroke:#333,stroke-width:2px; /* Enhanced Planner */
    end

    subgraph "Phase 3: Integration & Production"
        K; L;
        style E fill:#ccf,stroke:#333,stroke-width:2px; /* Expanded DB */
        style I fill:#f9d,stroke:#333,stroke-width:2px; /* Agents use real Tools */
    end

    %% Dashed lines could indicate data flow added/enhanced in later phases
    %% For simplicity, keeping the original solid lines.