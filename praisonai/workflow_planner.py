from typing import List, Dict, Any, Optional, Union
import uuid
import random
import logging
import json
import os
import re
import yaml
import time
from pathlib import Path
import importlib.util

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkflowPlanner")

class WorkflowPlanner:
    def __init__(self, project_brief: Dict):
        self.project_brief = project_brief
        self.brief_text = project_brief.get('project_brief', 'Create a startup')
        self.agent_templates = self._load_agent_templates()
        self.llm_client = None
        self.try_load_llm_client()
        
    def try_load_llm_client(self):
        """
        Пытается загрузить клиент LLM для генерации рабочих процессов.
        """
        try:
            # Пытаемся импортировать модуль для работы с OpenRouter
            if importlib.util.find_spec("openai"):
                import openai
                from openai import OpenAI
                
                # Проверяем наличие API-ключа
                api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
                if api_key:
                    # Создаем клиент OpenAI
                    self.llm_client = OpenAI(
                        api_key=api_key,
                        base_url="https://openrouter.ai/api/v1" if "OPENROUTER_API_KEY" in os.environ else None
                    )
                    logger.info("LLM client initialized successfully")
                else:
                    logger.warning("No API key found for LLM client")
            else:
                logger.warning("OpenAI module not found, LLM-based planning will not be available")
        except Exception as e:
            logger.error(f"Error initializing LLM client: {str(e)}")
        
    def _load_agent_templates(self) -> Dict[str, Dict]:
        """
        Загружает шаблоны агентов из YAML-файлов.
        """
        templates = {}
        
        # Пути для поиска шаблонов агентов
        search_paths = [
            "agents",
            "praisonai/agents",
            "."
        ]
        
        for path in search_paths:
            if not os.path.exists(path):
                continue
                
            for file in os.listdir(path):
                if file.endswith('.yaml') or file.endswith('.yml'):
                    try:
                        with open(os.path.join(path, file), 'r') as f:
                            agent_config = yaml.safe_load(f)
                            
                            # Проверяем, что это конфигурация агента
                            if 'name' in agent_config and 'description' in agent_config:
                                agent_type = file.split('.')[0]
                                templates[agent_type] = agent_config
                                logger.info(f"Loaded agent template: {agent_type}")
                    except Exception as e:
                        logger.error(f"Error loading agent template {file}: {str(e)}")
        
        # Если шаблоны не найдены, добавляем базовые шаблоны
        if not templates:
            templates = self._create_default_templates()
            
        return templates
        
    def _create_default_templates(self) -> Dict[str, Dict]:
        """
        Создает базовые шаблоны агентов.
        """
        return {
            "market_analyst": {
                "name": "Market Analyst",
                "description": "Analyzes market trends and opportunities",
                "capabilities": ["market_research", "competitor_analysis", "trend_identification"]
            },
            "product_designer": {
                "name": "Product Designer",
                "description": "Designs product features and user experience",
                "capabilities": ["feature_design", "ux_design", "wireframing"]
            },
            "developer": {
                "name": "Developer",
                "description": "Implements product features and functionality",
                "capabilities": ["coding", "testing", "debugging"]
            },
            "tester": {
                "name": "Tester",
                "description": "Tests product for bugs and usability issues",
                "capabilities": ["testing", "quality_assurance", "bug_reporting"]
            },
            "marketer": {
                "name": "Marketer",
                "description": "Creates and executes marketing campaigns",
                "capabilities": ["marketing_strategy", "content_creation", "campaign_management"]
            }
        }
        
    def plan_workflow(self) -> Dict:
        """
        Generate a workflow plan based on the project brief.
        """
        logger.info(f"Planning workflow for brief: {self.brief_text[:100]}...")
        
        try:
            # Если доступен LLM-клиент, используем его для генерации рабочего процесса
            if self.llm_client:
                return self.plan_workflow_with_llm()
            
            # Иначе используем правила для генерации рабочего процесса
            tasks = self.analyze_project_brief()
            workflow = self.determine_workflow(tasks)
            workflow_json = self.generate_workflow_json(workflow)
            
            return workflow_json
            
        except Exception as e:
            logger.error(f"Error planning workflow: {str(e)}", exc_info=True)
            # В случае ошибки возвращаем базовый рабочий процесс
            return self.generate_basic_workflow()

    def plan_workflow_with_llm(self) -> Dict:
        """
        Generate a workflow plan using LLM.
        """
        logger.info("Planning workflow with LLM")
        
        try:
            # Формируем запрос к LLM
            prompt = self._generate_llm_prompt()
            
            # Отправляем запрос к LLM
            response = self.llm_client.chat.completions.create(
                model="openai/gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a startup workflow planner. Your task is to analyze a project brief and generate a detailed workflow plan in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Извлекаем JSON из ответа
            content = response.choices[0].message.content
            workflow_json = self._extract_json_from_response(content)
            
            # Проверяем и дополняем полученный JSON
            if self._validate_workflow_json(workflow_json):
                logger.info("Successfully generated workflow with LLM")
                return workflow_json
            else:
                logger.warning("LLM generated invalid workflow JSON, falling back to rule-based planning")
                return self.generate_basic_workflow()
                
        except Exception as e:
            logger.error(f"Error in LLM workflow planning: {str(e)}", exc_info=True)
            return self.generate_basic_workflow()

    def _generate_llm_prompt(self) -> str:
        """
        Generate a prompt for the LLM.
        """
        # Список доступных агентов
        agent_descriptions = "\n".join([
            f"- {agent_type}: {config['name']} - {config['description']}"
            for agent_type, config in self.agent_templates.items()
        ])
        
        # Формат ожидаемого JSON
        # Note: This structure should be compatible with React Flow and LangGraph.
        # 'parallel' nodes act as entry points to a set of tasks that can run concurrently.
        # Edges should originate *from* the parallel node to the tasks within the block.
        # Edges should converge *to* a subsequent node *from* each task within the parallel block (or a joining node).
        # 'decision' nodes branch the workflow. They should have a 'condition' in data.
        # Edges originating from a decision node might represent 'true'/'false' paths or specific outcomes.
        json_format = """
{
  "nodes": [
    {
      "id": "task_market_analysis", // Unique ID
      "type": "default", // Node type: default, parallel, decision
      "data": {
        "label": "Market Analysis", // Display label
        "description": "Analyze market trends and opportunities", // Task description
        "agent_type": "market_analyst" // Assigned agent type
      },
      "position": {"x": 100, "y": 100} // Position for visualization
    },
    {
      "id": "parallel_dev",
      "type": "parallel",
      "data": { "label": "Parallel Development" },
      "position": {"x": 300, "y": 200}
    },
    {
      "id": "task_frontend",
      "type": "default",
      "data": { "label": "Frontend Dev", "agent_type": "developer" },
      "position": {"x": 500, "y": 150}
    },
    {
      "id": "task_backend",
      "type": "default",
      "data": { "label": "Backend Dev", "agent_type": "developer" },
      "position": {"x": 500, "y": 250}
    },
    {
      "id": "task_integration",
      "type": "default",
      "data": { "label": "Integration", "agent_type": "developer" },
      "position": {"x": 700, "y": 200}
    },
    {
      "id": "decision_quality_check",
      "type": "decision",
      "data": {
        "label": "Quality Check Passed?",
        "condition": "integration_test_results == 'success'" // Example condition
      },
      "position": {"x": 900, "y": 200}
    },
    {
      "id": "task_deploy",
      "type": "default",
      "data": { "label": "Deploy", "agent_type": "developer" },
      "position": {"x": 1100, "y": 150}
    },
     {
      "id": "task_fix_bugs",
      "type": "default",
      "data": { "label": "Fix Bugs", "agent_type": "developer" },
      "position": {"x": 1100, "y": 250}
    }
  ],
  "edges": [
    // Connect analysis to parallel block
    { "id": "e_analysis_parallel", "source": "task_market_analysis", "target": "parallel_dev" },
    // Edges *from* parallel block to tasks inside it
    { "id": "e_parallel_frontend", "source": "parallel_dev", "target": "task_frontend" },
    { "id": "e_parallel_backend", "source": "parallel_dev", "target": "task_backend" },
    // Edges *from* parallel tasks to the next step (integration)
    { "id": "e_frontend_integration", "source": "task_frontend", "target": "task_integration" },
    { "id": "e_backend_integration", "source": "task_backend", "target": "task_integration" },
    // Edge from integration to decision
    { "id": "e_integration_decision", "source": "task_integration", "target": "decision_quality_check" },
    // Edges from decision based on condition (example: true/false paths)
    { "id": "e_decision_deploy", "source": "decision_quality_check", "target": "task_deploy", "label": "Yes" }, // Label indicates condition outcome
    { "id": "e_decision_fix", "source": "decision_quality_check", "target": "task_fix_bugs", "label": "No" },
    // Edge from fixing bugs back to integration (example loop)
    { "id": "e_fix_integration", "source": "task_fix_bugs", "target": "task_integration" }
  ]
}
"""
        
        # Формируем полный запрос
        prompt = f"""
Analyze the following project brief and create a detailed workflow plan for a startup in JSON format suitable for React Flow and LangGraph execution.

PROJECT BRIEF:
{self.brief_text}

AVAILABLE AGENT TYPES:
{agent_descriptions}

INSTRUCTIONS:
1.  Identify the key tasks required based on the project brief.
2.  Structure these tasks into a logical workflow using nodes and edges.
3.  Use 'default' nodes for standard tasks, assigning an appropriate `agent_type` from the available list.
4.  Incorporate at least one 'parallel' node where multiple tasks can run concurrently. Edges should flow *from* the parallel node to the concurrent tasks, and *from* each concurrent task to the subsequent joining task or node.
5.  Incorporate at least one 'decision' node where the workflow branches. This node must have a `condition` field in its `data` object (e.g., "check_results == 'passed'"). Edges originating from the decision node should represent the different outcomes (e.g., using edge labels like "Yes"/"No" or "Success"/"Failure").
6.  Ensure all nodes have unique IDs (use descriptive prefixes like 'task_', 'parallel_', 'decision_').
7.  Define edges with unique IDs, specifying `source` and `target` node IDs. Ensure the graph is connected and logically sound (no dead ends unless intended, clear dependencies).
8.  Generate random `position` coordinates (x, y) for each node for visualization purposes (e.g., x between 0-1200, y between 0-800).

Your response MUST be ONLY the valid JSON object representing the workflow, adhering strictly to the following structure:
{json_format}

Do not include any introductory text, explanations, or markdown formatting around the JSON.
"""
        return prompt

    def _extract_json_from_response(self, response: str) -> Dict:
        """
        Extract JSON from LLM response.
        """
        # Ищем JSON в ответе
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Если JSON не обернут в маркеры кода, пробуем извлечь весь JSON
            json_str = response.strip()
            
            # Удаляем любой текст до первой фигурной скобки
            start_idx = json_str.find('{')
            if start_idx != -1:
                json_str = json_str[start_idx:]
                
            # Удаляем любой текст после последней фигурной скобки
            end_idx = json_str.rfind('}')
            if end_idx != -1:
                json_str = json_str[:end_idx+1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {str(e)}")
            logger.debug(f"Response content: {response}")
            return {}

    def _validate_workflow_json(self, workflow_json: Dict) -> bool:
        """
        Validate the workflow JSON structure.
        """
        # Проверяем наличие необходимых полей
        if 'nodes' not in workflow_json or 'edges' not in workflow_json:
            logger.error("Workflow JSON missing required fields: nodes, edges")
            return False
            
        # Проверяем, что узлы и ребра являются списками
        if not isinstance(workflow_json['nodes'], list) or not isinstance(workflow_json['edges'], list):
            logger.error("Workflow JSON nodes and edges must be lists")
            return False

        node_ids = set()
        edge_ids = set()
        all_node_ids = set()

        # Validate nodes
        for i, node in enumerate(workflow_json['nodes']):
            if not isinstance(node, dict):
                logger.error(f"Node at index {i} is not a dictionary: {node}")
                return False
            if not all(key in node for key in ['id', 'type', 'data', 'position']):
                logger.error(f"Node {node.get('id', f'at index {i}')} missing required fields (id, type, data, position): {node}")
                return False
            if not isinstance(node['id'], str) or not node['id']:
                logger.error(f"Node at index {i} has invalid or missing 'id': {node}")
                return False
            if node['id'] in node_ids:
                logger.error(f"Duplicate node ID found: {node['id']}")
                return False
            node_ids.add(node['id'])
            all_node_ids.add(node['id']) # Keep track for edge validation

            if not isinstance(node['type'], str) or not node['type']:
                 logger.error(f"Node {node['id']} has invalid or missing 'type': {node}")
                 return False
            if not isinstance(node['data'], dict):
                 logger.error(f"Node {node['id']} has invalid or missing 'data': {node}")
                 return False
            if not isinstance(node['position'], dict) or not all(key in node['position'] for key in ['x', 'y']):
                 logger.error(f"Node {node['id']} has invalid or missing 'position': {node}")
                 return False

            # Type-specific validation
            node_type = node['type']
            node_data = node['data']
            node_id = node['id']

            if node_type == 'decision':
                if 'condition' not in node_data or not isinstance(node_data['condition'], str) or not node_data['condition']:
                    logger.error(f"Decision node '{node_id}' missing or has invalid 'condition' in data: {node_data}")
                    return False
            elif node_type == 'parallel':
                # Parallel nodes primarily act as structural elements, data validation might be minimal
                if 'label' not in node_data or not isinstance(node_data['label'], str) or not node_data['label']:
                   logger.warning(f"Parallel node '{node_id}' missing 'label' in data: {node_data}") # Warning, not error
            elif node_type == 'default':
                if 'agent_type' not in node_data or not isinstance(node_data['agent_type'], str) or not node_data['agent_type']:
                    logger.error(f"Default node '{node_id}' missing or has invalid 'agent_type' in data: {node_data}")
                    return False
                if 'label' not in node_data or not isinstance(node_data['label'], str) or not node_data['label']:
                    logger.error(f"Default node '{node_id}' missing or has invalid 'label' in data: {node_data}")
                    return False
            # else: # Handle unknown node types if necessary
            #     logger.warning(f"Node '{node_id}' has unknown type '{node_type}'")

        # Validate edges
        for i, edge in enumerate(workflow_json['edges']):
            if not isinstance(edge, dict):
                logger.error(f"Edge at index {i} is not a dictionary: {edge}")
                return False
            if not all(key in edge for key in ['id', 'source', 'target']):
                logger.error(f"Edge {edge.get('id', f'at index {i}')} missing required fields (id, source, target): {edge}")
                return False
            if not isinstance(edge['id'], str) or not edge['id']:
                logger.error(f"Edge at index {i} has invalid or missing 'id': {edge}")
                return False
            if edge['id'] in edge_ids:
                logger.error(f"Duplicate edge ID found: {edge['id']}")
                return False
            edge_ids.add(edge['id'])

            if not isinstance(edge['source'], str) or not edge['source']:
                logger.error(f"Edge {edge['id']} has invalid or missing 'source': {edge}")
                return False
            if not isinstance(edge['target'], str) or not edge['target']:
                 logger.error(f"Edge {edge['id']} has invalid or missing 'target': {edge}")
                 return False

            # Check if source and target nodes exist
            if edge['source'] not in all_node_ids:
                logger.error(f"Edge {edge['id']} references non-existent source node: {edge['source']}")
                return False
            if edge['target'] not in all_node_ids:
                logger.error(f"Edge {edge['id']} references non-existent target node: {edge['target']}")
                return False

        logger.info("Workflow JSON structure validated successfully.")
        return True

    def generate_basic_workflow(self) -> Dict:
        """
        Generate a basic workflow as a fallback.
        """
        logger.info("Generating basic workflow")
        
        # Создаем базовые узлы
        market_analysis_id = f'market_analysis_{uuid.uuid4().hex[:8]}'
        product_design_id = f'product_design_{uuid.uuid4().hex[:8]}'
        development_id = f'development_{uuid.uuid4().hex[:8]}'
        testing_id = f'testing_{uuid.uuid4().hex[:8]}'
        deployment_id = f'deployment_{uuid.uuid4().hex[:8]}'
        
        nodes = [
            {
                'id': market_analysis_id,
                'type': 'default',
                'data': {
                    'label': 'Market Analysis',
                    'description': 'Analyze market trends and opportunities',
                    'agent_type': 'market_analyst'
                },
                'position': {'x': 250, 'y': 100}
            },
            {
                'id': product_design_id,
                'type': 'default',
                'data': {
                    'label': 'Product Design',
                    'description': 'Design the product based on market analysis',
                    'agent_type': 'product_designer'
                },
                'position': {'x': 250, 'y': 200}
            },
            {
                'id': development_id,
                'type': 'default',
                'data': {
                    'label': 'Development',
                    'description': 'Develop the product',
                    'agent_type': 'developer'
                },
                'position': {'x': 250, 'y': 300}
            },
            {
                'id': testing_id,
                'type': 'default',
                'data': {
                    'label': 'Testing',
                    'description': 'Test the product for bugs and usability issues',
                    'agent_type': 'tester'
                },
                'position': {'x': 250, 'y': 400}
            },
            {
                'id': deployment_id,
                'type': 'default',
                'data': {
                    'label': 'Deployment',
                    'description': 'Deploy the product to production',
                    'agent_type': 'developer'
                },
                'position': {'x': 250, 'y': 500}
            }
        ]
        
        # Создаем ребра
        edges = [
            {
                'id': f"{market_analysis_id}-{product_design_id}",
                'source': market_analysis_id,
                'target': product_design_id
            },
            {
                'id': f"{product_design_id}-{development_id}",
                'source': product_design_id,
                'target': development_id
            },
            {
                'id': f"{development_id}-{testing_id}",
                'source': development_id,
                'target': testing_id
            },
            {
                'id': f"{testing_id}-{deployment_id}",
                'source': testing_id,
                'target': deployment_id
            }
        ]
        
        return {'nodes': nodes, 'edges': edges}

    def analyze_project_brief(self) -> List[Dict]:
        """
        Analyze the project brief and identify the tasks to be performed.
        """
        logger.info("Analyzing project brief using rule-based approach")

        # Load task configuration from YAML file
        task_config_path = Path("praisonai") / "task_config.yaml"
        if not task_config_path.exists():
            logger.error(f"Task config file not found: {task_config_path}")
            return []  # Return empty list if config file is missing

        with open(task_config_path, 'r') as f:
            task_config = yaml.safe_load(f)
            if not task_config:
                logger.warning("Task config file is empty or invalid, using default tasks.")
                task_config = {} # Handle empty or invalid config gracefully

        default_tasks_config = task_config.get('default_tasks', [])
        keyword_tasks_config = task_config.get('keyword_tasks', {})
        dev_tasks_config = task_config.get('dev_tasks', []) # Load dev tasks config
        final_tasks_config = task_config.get('final_tasks', []) # Load final tasks config


        # Базовые задачи, которые всегда присутствуют
        base_tasks = []
        for task_def in default_tasks_config:
            base_tasks.append({
                'id': f"{task_def['id']}_{uuid.uuid4().hex[:8]}",
                'name': task_def['name'],
                'type': 'default',
                'description': task_def['description'],
                'agent_type': task_def['agent_type']
            })
        
        # Задачи разработки (from config)
        dev_tasks = []
        for task_def in dev_tasks_config:
             dev_tasks.append({
                'id': f"{task_def['id']}_{uuid.uuid4().hex[:8]}",
                'name': task_def['name'],
                'type': 'default',
                'description': task_def['description'],
                'agent_type': task_def['agent_type']
            })
        
        # Задачи тестирования и деплоя (from config)
        final_tasks = []
        for task_def in final_tasks_config:
             final_tasks.append({
                'id': f"{task_def['id']}_{uuid.uuid4().hex[:8]}",
                'name': task_def['name'],
                'type': 'default',
                'description': task_def['description'],
                'agent_type': task_def['agent_type']
            })
        
        # Дополнительные задачи в зависимости от проектного задания
        additional_tasks = []
        
        # Анализируем текст проектного задания для определения дополнительных задач
        brief_lower = self.brief_text.lower()
        
        # Keyword-based tasks from config
        for task_key, task_config in keyword_tasks_config.items():
            if any(keyword in brief_lower for keyword in task_config['keywords']):
                additional_tasks.append({
                    'id': f"{task_config['task']['id']}_{uuid.uuid4().hex[:8]}",
                    'name': task_config['task']['name'],
                    'type': 'default',
                    'description': task_config['task']['description'],
                    'agent_type': task_config['task']['agent_type']
                })
            
        
        # Объединяем все задачи
        all_tasks = base_tasks + dev_tasks + additional_tasks + final_tasks
        
        return all_tasks

    def determine_workflow(self, tasks: List[Dict]) -> Dict[str, Any]:
        """
        Determine the execution order and dependencies of the tasks using a more robust approach.
        """
        logger.info("Determining workflow structure based on analyzed tasks")

        # Define task categories more broadly
        # Development tasks include standard dev, database, and keyword-based dev tasks
        dev_keywords = ['dev', 'database', 'ai_model', 'blockchain', 'api', 'mobile', 'ar_vr']
        testing_keywords = ['testing', 'qa', 'test']
        deployment_keywords = ['deployment', 'deploy', 'release']
        marketing_keywords = ['marketing', 'launch', 'promotion']

        base_task_ids = set()
        dev_task_ids = set()
        testing_task_ids = set()
        deployment_task_ids = set()
        marketing_task_ids = set()
        other_task_ids = set()

        task_map = {task['id']: task for task in tasks} # Map ID to task dict for easy lookup

        # Categorize tasks
        for task in tasks:
            task_id_lower = task['id'].lower()
            if task['id'].startswith('market_analysis') or task['id'].startswith('product_design'):
                base_task_ids.add(task['id'])
            elif any(keyword in task_id_lower for keyword in dev_keywords):
                dev_task_ids.add(task['id'])
            elif any(keyword in task_id_lower for keyword in testing_keywords):
                testing_task_ids.add(task['id'])
            elif any(keyword in task_id_lower for keyword in deployment_keywords):
                deployment_task_ids.add(task['id'])
            elif any(keyword in task_id_lower for keyword in marketing_keywords):
                marketing_task_ids.add(task['id'])
            else:
                # If not categorized elsewhere, consider it 'other' for now
                # This might include tasks like 'data_analytics' if not caught by 'dev'
                other_task_ids.add(task['id'])
                # Re-evaluate if 'data_analytics' should be dev? Let's add it.
                if 'analytics' in task_id_lower:
                    dev_task_ids.add(task['id'])
                    other_task_ids.discard(task['id'])


        # --- Build Workflow Structure ---
        workflow_items = {} # Store nodes (tasks, parallel, decision) with dependencies
        last_base_task_id = None

        # 1. Add Base Tasks (Sequential)
        # Assuming default_tasks are always the first two from analyze_project_brief
        ordered_base_tasks = [t for t in tasks if t['id'] in base_task_ids]
        for i, task_id in enumerate(t['id'] for t in ordered_base_tasks):
            dependencies = [] if i == 0 else [ordered_base_tasks[i-1]['id']]
            workflow_items[task_id] = {'type': 'task', 'dependencies': dependencies}
            last_base_task_id = task_id

        # 2. Add Parallel Block for Development Tasks
        parallel_block_id = None
        if dev_task_ids:
            parallel_block_id = f'parallel_dev_{uuid.uuid4().hex[:8]}'
            parallel_deps = [last_base_task_id] if last_base_task_id else []
            workflow_items[parallel_block_id] = {'type': 'parallel', 'dependencies': parallel_deps}

            # Add dev tasks depending on the parallel block
            for task_id in dev_task_ids:
                workflow_items[task_id] = {'type': 'task', 'dependencies': [parallel_block_id]}

        # Determine dependencies for subsequent steps (post-development)
        # If there was a parallel block, subsequent tasks depend on ALL tasks within it.
        # Otherwise, they depend on the last base task.
        post_dev_dependencies = list(dev_task_ids) if parallel_block_id else ([last_base_task_id] if last_base_task_id else [])

        # 3. Add Other Tasks (Run sequentially after development)
        # Note: This assumes 'other' tasks don't need parallelization.
        last_other_task_id = None
        current_other_deps = post_dev_dependencies
        for task_id in other_task_ids: # Assuming order doesn't matter much here
             workflow_items[task_id] = {'type': 'task', 'dependencies': current_other_deps}
             current_other_deps = [task_id] # Next other task depends on this one
             last_other_task_id = task_id

        # Determine dependencies for testing (depends on dev and other tasks)
        testing_dependencies = [last_other_task_id] if last_other_task_id else post_dev_dependencies

        # 4. Add Testing Tasks (Run after dev/other tasks)
        # Assuming only one testing task for simplicity in rule-based approach
        testing_id = next(iter(testing_task_ids), None)
        if testing_id:
            workflow_items[testing_id] = {'type': 'task', 'dependencies': testing_dependencies}

        # 5. Add Decision Point (Optional, if testing and deployment exist)
        decision_point_id = None
        deployment_id = next(iter(deployment_task_ids), None)
        if testing_id and deployment_id:
            decision_point_id = f'decision_deploy_{uuid.uuid4().hex[:8]}'
            workflow_items[decision_point_id] = {
                'type': 'decision',
                'condition': 'testing_result == "success"', # Example condition
                'dependencies': [testing_id]
            }
            # Deployment now depends on the decision outcome
            deployment_dependencies = [decision_point_id]
        elif deployment_id:
             # Deploy directly after testing (if no decision) or after dev/other (if no testing)
             deployment_dependencies = [testing_id] if testing_id else testing_dependencies
        else:
            deployment_dependencies = [] # Should not happen if deployment_id exists

        # 6. Add Deployment Task
        if deployment_id:
             workflow_items[deployment_id] = {'type': 'task', 'dependencies': deployment_dependencies}

        # Determine dependencies for marketing (depends on deployment or testing)
        marketing_dependencies = [deployment_id] if deployment_id else ([testing_id] if testing_id else testing_dependencies)

        # 7. Add Marketing Tasks
        # Assuming one marketing task for simplicity
        marketing_id = next(iter(marketing_task_ids), None)
        if marketing_id:
            workflow_items[marketing_id] = {'type': 'task', 'dependencies': marketing_dependencies}


        # --- Finalize Workflow Structure for JSON Generation ---
        final_workflow = {
            'tasks': [],
            'parallel_blocks': [],
            'decision_points': []
        }

        for item_id, data in workflow_items.items():
            item_type = data['type']
            dependencies = data['dependencies']

            if item_type == 'task':
                task_info = task_map[item_id]
                final_workflow['tasks'].append({
                    **task_info,
                    'dependencies': dependencies
                })
            elif item_type == 'parallel':
                 final_workflow['parallel_blocks'].append({
                    'id': item_id,
                    'name': 'Parallel Development Block', # Generic name
                    'type': 'parallel',
                    'dependencies': dependencies
                 })
            elif item_type == 'decision':
                 final_workflow['decision_points'].append({
                    'id': item_id,
                    'name': 'Deployment Decision', # Generic name
                    'type': 'decision',
                    'condition': data.get('condition', 'unknown_condition'),
                    'dependencies': dependencies,
                    'tasks_inside': list(dev_task_ids) # Store IDs of tasks within this block
                 })
            elif item_type == 'decision':
                 # Store potential target IDs for different outcomes
                 # This is simplified; real logic might need more context
                 success_target = deployment_id if deployment_id else marketing_id # Example
                 failure_target = None # Or loop back, e.g., testing_id? Needs more rules.

                 final_workflow['decision_points'].append({
                    'id': item_id,
                    'name': 'Deployment Decision', # Generic name
                    'type': 'decision',
                    'condition': data.get('condition', 'unknown_condition'),
                    'dependencies': dependencies,
                    'success_target': success_target, # ID of node for 'true' branch
                    'failure_target': failure_target  # ID of node for 'false' branch
                 })

        logger.info(f"Determined workflow structure: {len(final_workflow['tasks'])} tasks, {len(final_workflow['parallel_blocks'])} parallel blocks, {len(final_workflow['decision_points'])} decision points")
        # Return the intermediate structure which is now richer
        # Return the intermediate structure which is now richer
        return final_workflow


    def generate_workflow_json(self, workflow_structure: Dict[str, Any]) -> Dict:
        """
        Generate the workflow JSON structure for ReactFlow based on the determined structure.
        """
        logger.info("Generating ReactFlow compatible JSON from workflow structure")
        nodes = []
        edges = []
        node_ids = set() # Keep track of added node IDs
        edge_ids = set() # Keep track of added edge IDs

        # Helper to generate positions (simple grid layout for now)
        pos_x, pos_y = 100, 100
        level_nodes = 0
        max_level_nodes = 4 # Nodes per row

        def get_next_position():
            nonlocal pos_x, pos_y, level_nodes
            current_pos = {'x': pos_x, 'y': pos_y}
            pos_x += 250
            level_nodes += 1
            if level_nodes >= max_level_nodes:
                pos_x = 100
                pos_y += 150
                level_nodes = 0
            # Add slight random offset
            current_pos['x'] += random.randint(-20, 20)
            current_pos['y'] += random.randint(-10, 10)
            return current_pos

        # Combine all items for easier processing
        all_items = (
            workflow_structure.get('tasks', []) +
            workflow_structure.get('parallel_blocks', []) +
            workflow_structure.get('decision_points', [])
        )
        item_map = {item['id']: item for item in all_items} # Map ID to item

        # --- Create Nodes ---
        for item in all_items:
            item_id = item['id']
            if item_id in node_ids: continue # Skip if already added (shouldn't happen with unique IDs)

            node_type = item.get('type', 'default') # Default, parallel, decision
            node_data = {'label': item.get('name', 'Unnamed Node')}

            if node_type == 'default':
                node_data['description'] = item.get('description', '')
                node_data['agent_type'] = item.get('agent_type', 'unknown')
            elif node_type == 'decision':
                node_data['condition'] = item.get('condition', 'unknown_condition')
            # Parallel nodes just need a label, already set

            nodes.append({
                'id': item_id,
                'type': node_type,
                'data': node_data,
                'position': get_next_position() # Use helper for positioning
            })
            node_ids.add(item_id)

        # --- Create Edges ---
        processed_dependencies = set() # Avoid duplicate edge creation logic

        for item_id, item_data in item_map.items():
            dependencies = item_data.get('dependencies', [])
            item_type = item_data.get('type')

            # Standard dependencies (Task -> Task, Task -> Parallel, Task -> Decision)
            for source_id in dependencies:
                 # Skip if source is a parallel block (handled separately)
                 if source_id in item_map and item_map[source_id].get('type') == 'parallel':
                     continue
                 # Skip if source is a decision block (handled separately)
                 if source_id in item_map and item_map[source_id].get('type') == 'decision':
                     continue

                 edge_id = f"e_{source_id}-{item_id}"
                 if edge_id not in edge_ids and source_id in node_ids and item_id in node_ids:
                     edges.append({
                         'id': edge_id,
                         'source': source_id,
                         'target': item_id
                     })
                     edge_ids.add(edge_id)

            # Special handling for Parallel Blocks
            if item_type == 'parallel':
                parallel_block_id = item_id
                tasks_inside = item_data.get('tasks_inside', [])

                # 1. Edges from Parallel Node to Tasks Inside
                for task_id in tasks_inside:
                    edge_id = f"e_{parallel_block_id}-{task_id}"
                    if edge_id not in edge_ids and parallel_block_id in node_ids and task_id in node_ids:
                        edges.append({
                            'id': edge_id,
                            'source': parallel_block_id,
                            'target': task_id
                        })
                        edge_ids.add(edge_id)

                # 2. Edges from Tasks Inside to Subsequent Nodes
                # Find nodes that depend on *all* tasks within this parallel block
                # This requires checking dependencies of all other nodes.
                # Simplified: Find nodes whose *only* dependencies are the tasks inside this block.
                # Even simpler for rule-based: Find the next sequential node(s) determined by determine_workflow
                # Let's find nodes that have *any* of the parallel tasks as a dependency (might create extra edges if complex branching)
                # A better way: Find nodes whose dependencies list *equals* tasks_inside set.

                # Find subsequent nodes (those depending on tasks inside the block)
                subsequent_nodes = []
                for potential_target_id, potential_target_data in item_map.items():
                    if potential_target_id == parallel_block_id or potential_target_id in tasks_inside:
                        continue # Skip self and tasks inside
                    target_deps = set(potential_target_data.get('dependencies', []))
                    # Check if the target's dependencies *are exactly* the set of tasks inside the parallel block
                    # Or if the target depends on the parallel block ID itself (if we adapt determine_workflow)
                    # Current determine_workflow makes subsequent tasks depend on the *list* of task IDs.
                    if target_deps == set(tasks_inside):
                         subsequent_nodes.append(potential_target_id)


                # If no node depends *exactly* on all parallel tasks, find nodes that depend on the *last* task added in determine_workflow logic
                # This is brittle. Let's assume determine_workflow correctly sets dependencies.
                # We need to find the node(s) that depend on the parallel tasks.
                # The current `determine_workflow` sets dependencies like testing_dependencies = post_dev_dependencies
                # where post_dev_dependencies = list(dev_task_ids)

                # Find nodes whose dependency list is exactly the list of tasks inside
                target_ids_for_parallel_output = []
                for check_id, check_data in item_map.items():
                    if set(check_data.get('dependencies', [])) == set(tasks_inside):
                        target_ids_for_parallel_output.append(check_id)


                for task_id in tasks_inside:
                    for target_id in target_ids_for_parallel_output:
                         edge_id = f"e_{task_id}-{target_id}"
                         if edge_id not in edge_ids and task_id in node_ids and target_id in node_ids:
                             edges.append({
                                 'id': edge_id,
                                 'source': task_id,
                                 'target': target_id
                             })
                             edge_ids.add(edge_id)


            # Special handling for Decision Points
            if item_type == 'decision':
                decision_id = item_id
                success_target = item_data.get('success_target')
                failure_target = item_data.get('failure_target') # Currently None in determine_workflow

                if success_target and success_target in node_ids:
                    edge_id = f"e_{decision_id}-{success_target}_yes"
                    if edge_id not in edge_ids:
                        edges.append({
                            'id': edge_id,
                            'source': decision_id,
                            'target': success_target,
                            'label': 'Yes / Success' # Label for clarity
                        })
                        edge_ids.add(edge_id)

                if failure_target and failure_target in node_ids:
                    edge_id = f"e_{decision_id}-{failure_target}_no"
                    if edge_id not in edge_ids:
                         edges.append({
                            'id': edge_id,
                            'source': decision_id,
                            'target': failure_target,
                            'label': 'No / Failure' # Label for clarity
                         })
                         edge_ids.add(edge_id)
                # If no failure target, the 'No' path might just end or loop back - needs more rules.


        logger.info(f"Generated {len(nodes)} nodes and {len(edges)} edges for ReactFlow.")
        return {'nodes': nodes, 'edges': edges}
