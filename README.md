<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/logo/dark.png" />
    <source media="(prefers-color-scheme: light)" srcset="docs/logo/light.png" />
    <img alt="PraisonAI Logo" src="docs/logo/light.png" />
  </picture>
</p>

<p align="center">
<a href="https://github.com/MervinPraison/PraisonAI"><img src="https://static.pepy.tech/badge/PraisonAI" alt="Total Downloads" /></a>
<a href="https://github.com/MervinPraison/PraisonAI"><img src="https://img.shields.io/github/v/release/MervinPraison/PraisonAI" alt="Latest Stable Version" /></a>
<a href="https://github.com/MervinPraison/PraisonAI"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" /></a>
</p>

<div align="center">

# Praison AI

<a href="https://trendshift.io/repositories/9130" target="_blank"><img src="https://trendshift.io/api/badge/repositories/9130" alt="MervinPraison%2FPraisonAI | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>

PraisonAI is a production-ready Multi-AI Agents framework with self-reflection, designed to create AI Agents to automate and solve problems ranging from simple tasks to complex challenges. By integrating PraisonAI Agents, AutoGen, and CrewAI into a low-code solution, it streamlines the building and management of multi-agent LLM systems, emphasising simplicity, customisation, and effective human-agent collaboration.

<div align="center">
  <a href="https://docs.praison.ai">
    <p align="center">
      <img src="https://img.shields.io/badge/📚_Documentation-Visit_docs.praison.ai-blue?style=for-the-badge&logo=bookstack&logoColor=white" alt="Documentation" />
    </p>
  </a>
</div>

## Key Features

- 🤖 Automated AI Agents Creation
- 🔄 Self Reflection AI Agents
- 🧠 Reasoning AI Agents
- 👁️ Multi Modal AI Agents
- 🤝 Multi Agent Collaboration
- 🎭 AI Agent Workflow
- 📚 Add Custom Knowledge
- 🧠 Agents with Short and Long Term Memory
- 📄 Chat with PDF Agents
- 💻 Code Interpreter Agents
- 📚 RAG Agents
- 🤔 Async & Parallel Processing
- 🔄 Auto Agents
- 🔢 Math Agents
- 🎯 Structured Output Agents
- 🔗 LangChain Integrated Agents
- 📞 Callback Agents
- 🤏 Mini AI Agents
- 🛠️ 100+ Custom Tools
- 📄 YAML Configuration
- 💯 100+ LLM Support

## Project Structure

PraisonAI follows a modular architecture designed for scalability and flexibility:

```
PraisonAI/
├── backend/              # Core backend services
│   └── api.py            # Main FastAPI application
├── praisonai/            # Core framework
│   ├── workflow_planner.py # Workflow planning engine
│   └── agents_generator.py # Agent generation logic
├── ui/                   # Real-time monitoring interface
│   ├── realtime.py       # Real-time execution monitoring
│   ├── db.py            # Database operations
│   └── components/      # UI components
├── config.yaml           # Main configuration
├── agents.yaml           # Agent configurations
├── docker/               # Containerization
├── docs/                 # Documentation
└── examples/             # Usage examples
```

Key Components:
- **[Workflow Planner](praisonai/workflow_planner.py)** - Core logic for planning agent workflows
- **[Agents Generator](praisonai/agents_generator.py)** - Creates and manages agent instances
- **[Realtime Monitoring](ui/realtime.py)** - Tracks execution with:
  - SQLite persistence for state tracking
  - Chainlit integration for visual monitoring
  - Event handlers for conversation updates
- **[API Endpoints](backend/api.py)** - REST interface for managing workflows
- **[Configuration](config.yaml)** - Centralized project configuration

## Using Python Code

### Research Analyst Agent
```python
from praisonai import PraisonAI

agent = PraisonAI(
    agents_config="docs/agents/research-analyst.mdx",
    framework="praisonai"
)

result = agent.start({
    "urls": ["https://example.com"],
    "topic": "Your research topic"
})
```

### Key Features:
- Web scraping with CSS selector support
- AI-powered text analysis via OpenRouter
- Persistent result storage in Supabase
- Built-in error handling and retries
- Complete test coverage (pytest)
- Example implementation (examples/research_analyst_demo.py)

### Requirements:
```bash
pip install beautifulsoup4 requests openai supabase python-dotenv pytest
```

Light weight package dedicated for coding:
```bash
pip install praisonaiagents
```

```bash
export OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxx
```

### 1. Single Agent

Create app.py file and add the code below:
```python
from praisonaiagents import Agent
agent = Agent(instructions="Your are a helpful AI assistant")
agent.start("Write a movie script about a robot in Mars")
```

Run:
```bash
python app.py
```

### 2. Multi Agents

Create app.py file and add the code below:
```python
from praisonaiagents import Agent, PraisonAIAgents

research_agent = Agent(instructions="Research about AI")
summarise_agent = Agent(instructions="Summarise research agent's findings")
agents = PraisonAIAgents(agents=[research_agent, summarise_agent])
agents.start()
```

Run:
```bash
python app.py
```

## Using No Code

### Auto Mode:
```bash
pip install praisonai
export OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxx
praisonai --auto create a movie script about Robots in Mars
```

## Using JavaScript Code

```bash
npm install praisonai
export OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxx
```

```javascript
const { Agent } = require('praisonai');
const agent = new Agent({ instructions: 'You are a helpful AI assistant' });
agent.start('Write a movie script about a robot in Mars');
```

![PraisonAI CLI Demo](docs/demo/praisonai-cli-demo.gif)

## AI Agents Flow

```mermaid
graph LR
    %% Define the main flow
    Start([▶ Start]) --> Agent1
    Agent1 --> Process[⚙ Process]
    Process --> Agent2
    Agent2 --> Output([✓ Output])
    Process -.-> Agent1
    
    %% Define subgraphs for agents and their tasks
    subgraph Agent1[ ]
        Task1[📋 Task]
        AgentIcon1[🤖 AI Agent]
        Tools1[🔧 Tools]
        
        Task1 --- AgentIcon1
        AgentIcon1 --- Tools1
    end
    
    subgraph Agent2[ ]
        Task2[📋 Task]
        AgentIcon2[🤖 AI Agent]
        Tools2[🔧 Tools]
        
        Task2 --- AgentIcon2
        AgentIcon2 --- Tools2
    end

    classDef input fill:#8B0000,stroke:#7C90A0,color:#fff
    classDef process fill:#189AB4,stroke:#7C90A0,color:#fff
    classDef tools fill:#2E8B57,stroke:#7C90A0,color:#fff
    classDef transparent fill:none,stroke:none

    class Start,Output,Task1,Task2 input
    class Process,AgentIcon1,AgentIcon2 process
    class Tools1,Tools2 tools
    class Agent1,Agent2 transparent
```

## AI Agents with Tools

Create AI agents that can use tools to interact with external systems and perform actions.

```mermaid
flowchart TB
    subgraph Tools
        direction TB
        T3[Internet Search]
        T1[Code Execution]
        T2[Formatting]
    end

    Input[Input] ---> Agents
    subgraph Agents
        direction LR
        A1[Agent 1]
        A2[Agent 2]
        A3[Agent 3]
    end
    Agents ---> Output[Output]

    T3 --> A1
    T1 --> A2
    T2 --> A3

    style Tools fill:#189AB4,color:#fff
    style Agents fill:#8B0000,color:#fff
    style Input fill:#8B0000,color:#fff
    style Output fill:#8B0000,color:#fff
```

## AI Agents with Memory

Create AI agents with memory capabilities for maintaining context and information across tasks.

```mermaid
flowchart TB
    subgraph Memory
        direction TB
        STM[Short Term]
        LTM[Long Term]
    end

    subgraph Store
        direction TB
        DB[(Vector DB)]
    end

    Input[Input] ---> Agents
    subgraph Agents
        direction LR
        A1[Agent 1]
        A2[Agent 2]
        A3[Agent 3]
    end
    Agents ---> Output[Output]

    Memory <--> Store
    Store <--> A1
    Store <--> A2
    Store <--> A3

    style Memory fill:#189AB4,color:#fff
    style Store fill:#2E8B57,color:#fff
    style Agents fill:#8B0000,color:#fff
    style Input fill:#8B0000,color:#fff
    style Output fill:#8B0000,color:#fff
```

## AI Agents with Different Processes

### Sequential Process

The simplest form of task execution where tasks are performed one after another.

```mermaid
graph LR
    Input[Input] --> A1
    subgraph Agents
        direction LR
        A1[Agent 1] --> A2[Agent 2] --> A3[Agent 3]
    end
    A3 --> Output[Output]

    classDef input fill:#8B0000,stroke:#7C90A0,color:#fff
    classDef process fill:#189AB4,stroke:#7C90A0,color:#fff
    classDef transparent fill:none,stroke:none

    class Input,Output input
    class A1,A2,A3 process
    class Agents transparent
```

### Hierarchical Process

Uses a manager agent to coordinate task execution and agent assignments.

```mermaid
graph TB
    Input[Input] --> Manager
    
    subgraph Agents
        Manager[Manager Agent]
        
        subgraph Workers
            direction LR
            W1[Worker 1]
            W2[Worker 2]
            W3[Worker 3]
        end
        
        Manager --> W1
        Manager --> W2
        Manager --> W3
    end
    
    W1 --> Manager
    W2 --> Manager
    W3 --> Manager
    Manager --> Output[Output]

    classDef input fill:#8B0000,stroke:#7C90A0,color:#fff
    classDef process fill:#189AB4,stroke:#7C90A0,color:#fff
    classDef transparent fill:none,stroke:none

    class Input,Output input
    class Manager,W1,W2,W3 process
    class Agents,Workers transparent
```

### Workflow Process

Advanced process type supporting complex task relationships and conditional execution.

```mermaid
graph LR
    Input[Input] --> Start
    
    subgraph Workflow
        direction LR
        Start[Start] --> C1{Condition}
        C1 --> |Yes| A1[Agent 1]
        C1 --> |No| A2[Agent 2]
        A1 --> Join
        A2 --> Join
        Join --> A3[Agent 3]
    end
    
    A3 --> Output[Output]

    classDef input fill:#8B0000,stroke:#7C90A0,color:#fff
    classDef process fill:#189AB4,stroke:#7C90A0,color:#fff
    classDef decision fill:#2E8B57,stroke:#7C90A0,color:#fff
    classDef transparent fill:none,stroke:none

    class Input,Output input
    class Start,A1,A2,A3,Join process
    class C1 decision
    class Workflow transparent
```

#### Agentic Routing Workflow

Create AI agents that can dynamically route tasks to specialized LLM instances.

```mermaid
flowchart LR
    In[In] --> Router[LLM Call Router]
    Router --> LLM1[LLM Call 1]
    Router --> LLM2[LLM Call 2]
    Router --> LLM3[LLM Call 3]
    LLM1 --> Out[Out]
    LLM2 --> Out
    LLM3 --> Out
    
    style In fill:#8B0000,color:#fff
    style Router fill:#2E8B57,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

#### Agentic Orchestrator Worker

Create AI agents that orchestrate and distribute tasks among specialized workers.

```mermaid
flowchart LR
    In[In] --> Router[LLM Call Router]
    Router --> LLM1[LLM Call 1]
    Router --> LLM2[LLM Call 2]
    Router --> LLM3[LLM Call 3]
    LLM1 --> Synthesizer[Synthesizer]
    LLM2 --> Synthesizer
    LLM3 --> Synthesizer
    Synthesizer --> Out[Out]
    
    style In fill:#8B0000,color:#fff
    style Router fill:#2E8B57,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Synthesizer fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

#### Agentic Autonomous Workflow

Create AI agents that can autonomously monitor, act, and adapt based on environment feedback.

```mermaid
flowchart LR
    Human[Human] <--> LLM[LLM Call]
    LLM -->|ACTION| Environment[Environment]
    Environment -->|FEEDBACK| LLM
    LLM --> Stop[Stop]
    
    style Human fill:#8B0000,color:#fff
    style LLM fill:#2E8B57,color:#fff
    style Environment fill:#8B0000,color:#fff
    style Stop fill:#333,color:#fff
```

#### Agentic Parallelization

Create AI agents that can execute tasks in parallel for improved performance.

```mermaid
flowchart LR
    In[In] --> LLM2[LLM Call 2]
    In --> LLM1[LLM Call 1]
    In --> LLM3[LLM Call 3]
    LLM1 --> Aggregator[Aggregator]
    LLM2 --> Aggregator
    LLM3 --> Aggregator
    Aggregator --> Out[Out]
    
    style In fill:#8B0000,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Aggregator fill:#fff,color:#000
    style Out fill:#8B0000,color:#fff
```

#### Agentic Prompt Chaining

Create AI agents with sequential prompt chaining for complex workflows.

```mermaid
flowchart LR
    In[In] --> LLM1[LLM Call 1] --> Gate{Gate}
    Gate --> |Pass| LLM2[LLM Call 2] --> |Output 2| LLM3[LLM Call 3] --> Out[Out]
    Gate --> |Fail| Exit[Exit]
    
    style In fill:#8B0000,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
    style Exit fill:#8B0000,color:#fff
```

#### Agentic Evaluator Optimizer

Create AI agents that can generate and optimize solutions through iterative feedback.

```mermaid
flowchart LR
    In[In] --> Generator[LLM Call Generator] 
    Generator --> |SOLUTION| Evaluator[LLM Call Evaluator] --> |ACCEPTED| Out[Out]
    Evaluator --> |REJECTED + FEEDBACK| Generator
    
    style In fill:#8B0000,color:#fff
    style Generator fill:#2E8B57,color:#fff
    style Evaluator fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

#### Repetitive Agents

Create AI agents that can efficiently handle repetitive tasks through automated loops.

```mermaid
flowchart LR
    In[Input] --> LoopAgent[("Looping Agent")]
    LoopAgent --> Task[Task]
    Task --> |Next iteration| LoopAgent
    Task --> |Done| Out[Output]
    
    style In fill:#8B0000,color:#fff
    style LoopAgent fill:#2E8B57,color:#fff,shape:circle
    style Task fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

## Adding Models

<div align="center">
  <a href="https://docs.praison.ai/models">
    <p align="center">
      <img src="https://img.shields.io/badge/%F0%9F%93%9A_Models-Visit_docs.praison.ai-blue?style=for-the-badge&logo=bookstack&logoColor=white" alt="Models" />
    </p>
  </a>
</div>

## Ollama Integration
```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
```

## Groq Integration
Replace xxxx with Groq API KEY:
```bash
export OPENAI_API_KEY=xxxxxxxxxxx
export OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

## No Code Options

## Agents Playbook

### Simple Playbook Example

Create `agents.yaml` file and add the code below:

```yaml
framework: praisonai
topic: Artificial Intelligence
roles:
  screenwriter:
    backstory: "Skilled in crafting scripts with engaging dialogue about {topic}."
    goal: Create scripts from concepts.
    role: Screenwriter
    tasks:
      scriptwriting_task:
        description: "Write a script about {topic}"
        expected_output: "Complete script with dialogue"
```

<Note>
You can automatically create `agents.yaml` file using
```bash
praisonai --init "your task description"
```
</Note>

## Use 100+ Models

PraisonAI supports all major LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Groq (Llama, Mixtral)
- Ollama (local models)
- And many more...

See full list in [Models Documentation](https://docs.praison.ai/models)

## Development:

```bash
git clone https://github.com/MervinPraison/PraisonAI.git
cd PraisonAI
pip install -e .
```

# Install with extras

```bash
pip install "praisonai[ui,crewai,autogen]"
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://docs.praison.ai/contributing) for details.

## Other Features

- **Self Reflection**: Agents can evaluate and improve their own outputs
- **Multi-Modal**: Support for text, image, and audio processing
- **Custom Tools**: Easily add your own tools and integrations
- **Workflow Visualization**: Built-in visualization of agent workflows

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=MervinPraison/PraisonAI&type=Date)](https://star-history.com/#MervinPraison/PraisonAI&Date)

## Video Tutorials

Coming soon! Check our [YouTube channel](https://youtube.com/@praisonai) for updates.
