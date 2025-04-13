from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future
import os
import json
import datetime
import uuid
import importlib
import logging
import yaml
import time
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LangGraphExecutor")

class LangGraphExecutor:
    def __init__(self, workflow: Dict, workflow_id: Optional[str] = None):
        self.workflow = workflow
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.executor = ThreadPoolExecutor()
        self.results = []
        self.context = {}  # Контекст выполнения для хранения результатов задач
        self.agent_cache = {}  # Кэш для хранения экземпляров агентов
        self.task_results = {}  # Результаты выполнения задач

    def execute_workflow(self):
        """
        Execute the workflow plan.
        """
        # Создаем запись о начале выполнения рабочего процесса
        execution_id = str(uuid.uuid4())
        start_time = datetime.datetime.now().isoformat()
        
        try:
            logger.info(f"Starting workflow execution: {self.workflow_id}")
            
            # Создаем топологическую сортировку узлов для правильного порядка выполнения
            execution_order = self._create_execution_order()
            
            # Выполняем узлы в правильном порядке
            for node_id in execution_order:
                node = self._find_node_by_id(node_id)
                if not node:
                    continue
                    
                # Проверяем, выполнены ли все зависимости
                dependencies_met = self._check_dependencies(node)
                if not dependencies_met:
                    logger.warning(f"Skipping node {node_id} due to unmet dependencies")
                    continue
                
                # Выполняем узел в зависимости от его типа
                if node.get('type') == 'parallel':
                    self.execute_parallel_block(node)
                elif node.get('type') == 'decision':
                    self.execute_decision_point(node)
                else:
                    self.execute_task(node)
            
            # Записываем успешное завершение
            self._save_result(execution_id, start_time, 'completed', {
                'message': 'Workflow executed successfully',
                'tasks_completed': len(execution_order),
                'results': self.task_results
            })
            
            return {
                'status': 'completed',
                'execution_id': execution_id,
                'message': 'Workflow executed successfully',
                'results': self.task_results
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            
            # Записываем ошибку
            self._save_result(execution_id, start_time, 'failed', {
                'error': str(e),
                'message': 'Workflow execution failed'
            })
            
            raise e

    def _find_node_by_id(self, node_id: str) -> Optional[Dict]:
        """
        Find a node in the workflow by its ID.
        """
        for node in self.workflow.get('nodes', []):
            if node.get('id') == node_id:
                return node
        return None

    def _create_execution_order(self) -> List[str]:
        """
        Create a topological sort of the nodes based on dependencies.
        """
        # Создаем граф зависимостей
        graph = {}
        for node in self.workflow.get('nodes', []):
            node_id = node.get('id')
            if not node_id:
                continue
                
            graph[node_id] = []
            
        # Заполняем граф зависимостями
        for edge in self.workflow.get('edges', []):
            source = edge.get('source')
            target = edge.get('target')
            if source and target:
                if target in graph:
                    graph[target].append(source)
        
        # Выполняем топологическую сортировку
        visited = set()
        temp = set()
        order = []
        
        def visit(node_id):
            if node_id in temp:
                raise ValueError(f"Cycle detected in workflow graph at node {node_id}")
            if node_id in visited:
                return
                
            temp.add(node_id)
            
            # Посещаем все зависимости
            for dependency in graph.get(node_id, []):
                visit(dependency)
                
            temp.remove(node_id)
            visited.add(node_id)
            order.append(node_id)
        
        # Посещаем все узлы
        for node_id in graph:
            if node_id not in visited:
                visit(node_id)
                
        # Возвращаем обратный порядок для правильной последовательности выполнения
        return list(reversed(order))

    def _check_dependencies(self, node: Dict) -> bool:
        """
        Check if all dependencies of a node are met.
        """
        # Получаем зависимости из ребер
        dependencies = []
        for edge in self.workflow.get('edges', []):
            if edge.get('target') == node.get('id'):
                dependencies.append(edge.get('source'))
        
        # Проверяем, выполнены ли все зависимости
        for dependency in dependencies:
            if dependency not in self.task_results:
                return False
                
            # Проверяем успешность выполнения зависимости
            if self.task_results[dependency].get('status') != 'success':
                return False
                
        return True

    def execute_task(self, task: Dict):
        """
        Execute a single task using a PraisonAI agent.
        """
        task_id = task.get('id')
        task_type = task.get('type', 'default')
        task_data = task.get('data', {})
        
        logger.info(f"Executing task: {task_id} ({task_data.get('label', 'Unnamed Task')})")
        
        try:
            # Определяем тип агента на основе данных задачи
            agent_type = task_data.get('agent_type', 'default')
            
            # Получаем или создаем экземпляр агента
            agent = self._get_agent(agent_type)
            
            # Подготавливаем входные данные для агента
            input_data = {
                'task': task_data,
                'context': self.context,
                'workflow_id': self.workflow_id
            }
            
            # Выполняем агента
            start_time = time.time()
            result = self._run_agent(agent, input_data)
            execution_time = time.time() - start_time
            
            # Обновляем контекст выполнения
            if isinstance(result, dict):
                self.context.update(result)
            
            # Сохраняем результат выполнения задачи
            self.task_results[task_id] = {
                'status': 'success',
                'result': result,
                'execution_time': execution_time
            }
            
            logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}", exc_info=True)
            
            # Сохраняем информацию об ошибке
            self.task_results[task_id] = {
                'status': 'error',
                'error': str(e)
            }
            
            # В зависимости от настроек, можем либо продолжить выполнение, либо прервать его
            if task_data.get('critical', False):
                raise e

    def _get_agent(self, agent_type: str) -> Any:
        """
        Get or create an agent instance based on the agent type.
        """
        if agent_type in self.agent_cache:
            return self.agent_cache[agent_type]
            
        # Ищем YAML-файл с определением агента
        agent_yaml_path = self._find_agent_yaml(agent_type)
        if not agent_yaml_path:
            logger.warning(f"Agent YAML not found for type: {agent_type}, using placeholder")
            # Возвращаем заглушку агента
            return self._create_placeholder_agent(agent_type)
            
        # Загружаем определение агента из YAML
        with open(agent_yaml_path, 'r') as f:
            agent_config = yaml.safe_load(f)
            
        # Создаем экземпляр агента
        agent = self._create_agent_from_config(agent_config)
        
        # Кэшируем агента для повторного использования
        self.agent_cache[agent_type] = agent
        
        return agent

    def _find_agent_yaml(self, agent_type: str) -> Optional[str]:
        """
        Find the YAML file for the specified agent type.
        """
        # Ищем в стандартных директориях
        search_paths = [
            "agents",
            "praisonai/agents",
            "."
        ]
        
        for path in search_paths:
            yaml_path = os.path.join(path, f"{agent_type}.yaml")
            if os.path.exists(yaml_path):
                return yaml_path
                
        return None

    def _create_agent_from_config(self, config: Dict) -> Any:
        """
        Create an agent instance from a configuration dictionary.
        """
        # Здесь должна быть логика создания агента PraisonAI из конфигурации
        # --- Implementation for creating PraisonAI agent ---
        try:
            # Assuming PraisonAI has a standard way to initialize from config
            # This might involve importing a specific class or factory function
            # For example, let's assume there's a `PraisonAgent` class
            # We need to import it. This might require knowing the PraisonAI structure.
            # Let's try a dynamic import based on a conventional path or config value
            
            # Placeholder: Assuming a PraisonAI class exists
            # from praisonai import PraisonAgent # Adjust import as needed
            
            # This part needs the actual PraisonAI agent class/factory
            # For now, we'll simulate creating an object that has a 'run' method
            class MockPraisonAgent:
                def __init__(self, config, workflow_id, task_id):
                    self.config = config
                    self.name = config.get('name', 'UnnamedAgent')
                    self.workflow_id = workflow_id
                    self.task_id = task_id
                    logger.info(f"Initialized MockPraisonAgent: {self.name} for task {self.task_id}")

                def run(self, input_data: Dict) -> Any:
                    logger.info(f"MockPraisonAgent '{self.name}' (Task: {self.task_id}) running with input: {input_data.get('task', {}).get('label', 'N/A')}")
                    # Simulate agent work
                    time.sleep(random.uniform(0.5, 1.5))
                    result = {
                        'agent_name': self.name,
                        'status': 'simulated_success',
                        'output': f"Simulated output for {input_data.get('task', {}).get('label', 'N/A')}",
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    # Simulate updating context
                    self.update_context(input_data['context'], result)
                    return result # Agent should return its results

                def update_context(self, context, result):
                    # Agents might update the shared context based on their results
                    context[f"{self.task_id}_output"] = result.get('output')
                    context[f"{self.task_id}_status"] = result.get('status')
                    logger.debug(f"Context updated by {self.name} (Task: {self.task_id})")


            # Get task ID from the config if possible, or generate one
            # Note: The config passed here is the agent's config from YAML,
            # not the task node config from the workflow.
            # We need the task context here. Let's refine _get_agent call.
            # --> Refactoring needed: _get_agent should probably receive task context.
            # --> For now, pass workflow_id and a generic task marker.
            agent_instance = MockPraisonAgent(config, self.workflow_id, f"agent_{config.get('name', 'unknown')}")
            return agent_instance

        except ImportError:
             logger.error("Failed to import PraisonAI agent class. Ensure PraisonAI is installed and configured correctly.")
             raise
        except Exception as e:
            logger.error(f"Error creating agent from config {config.get('name', 'N/A')}: {str(e)}", exc_info=True)
            raise

    # Removed _create_placeholder_agent as it's replaced by MockPraisonAgent logic within _create_agent_from_config

    def _run_agent(self, agent: Any, input_data: Dict) -> Any:
        """
        Run the PraisonAI agent instance with the provided input data.
        Assumes the agent instance has a 'run' method.
        """
        if hasattr(agent, 'run') and callable(agent.run):
            try:
                # Pass the relevant input data expected by the PraisonAI agent's run method
                # This likely includes the specific task details and the shared context
                return agent.run(input_data)
            except Exception as e:
                agent_name = getattr(agent, 'name', 'UnknownAgent')
                logger.error(f"Error during execution of agent '{agent_name}': {str(e)}", exc_info=True)
                # Re-raise the exception to be caught by execute_task
                raise
        else:
            # This case should ideally not happen if _create_agent_from_config works
            logger.error(f"Agent object of type {type(agent)} does not have a callable 'run' method.")
            raise ValueError(f"Invalid agent object: {agent}. Expected an object with a 'run' method.")


    def execute_parallel_block(self, parallel_block: Dict):
        """
        Execute a parallel block of tasks.
        """
        block_id = parallel_block.get('id')
        logger.info(f"Executing parallel block: {block_id} ({parallel_block.get('data', {}).get('label', 'Unnamed Block')})")
        
        # Находим все задачи, которые зависят от этого параллельного блока
        dependent_tasks = []
        for edge in self.workflow.get('edges', []):
            if edge.get('source') == block_id:
                target_node = self._find_node_by_id(edge.get('target'))
                if target_node:
                    dependent_tasks.append(target_node)
        
        # Запускаем задачи параллельно
        futures: List[Future] = []
        for task in dependent_tasks:
            futures.append(self.executor.submit(self.execute_task, task))
        
        # Ждем завершения всех задач
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in parallel task: {str(e)}", exc_info=True)
                
        logger.info(f"Parallel block {block_id} completed")
        
        # Сохраняем результат выполнения блока
        self.task_results[block_id] = {
            'status': 'success',
            'message': f"Parallel block executed with {len(dependent_tasks)} tasks"
        }

    def execute_decision_point(self, decision_point: Dict):
        """
        Execute a decision point in the workflow.
        """
        decision_id = decision_point.get('id')
        logger.info(f"Executing decision point: {decision_id} ({decision_point.get('data', {}).get('label', 'Unnamed Decision')})")
        
        # Получаем условие из данных точки принятия решения
        condition = decision_point.get('data', {}).get('condition', '')
        
        # Оцениваем условие
        result = self.evaluate_decision(decision_point, condition)
        
        # Находим все возможные пути после точки принятия решения
        paths = {}
        for edge in self.workflow.get('edges', []):
            if edge.get('source') == decision_id:
                target_node = self._find_node_by_id(edge.get('target'))
                if target_node:
                    # Проверяем, есть ли у ребра условие
                    edge_condition = edge.get('data', {}).get('condition')
                    paths[edge_condition or 'default'] = target_node
        
        # Выбираем путь на основе результата оценки условия
        if result and 'true' in paths:
            logger.info(f"Decision {decision_id} evaluated to TRUE, taking 'true' path")
            self.execute_task(paths['true'])
        elif not result and 'false' in paths:
            logger.info(f"Decision {decision_id} evaluated to FALSE, taking 'false' path")
            self.execute_task(paths['false'])
        elif 'default' in paths:
            logger.info(f"Decision {decision_id} taking default path")
            self.execute_task(paths['default'])
        else:
            logger.warning(f"Decision {decision_id} has no valid paths for result: {result}")
        
        # Сохраняем результат выполнения точки принятия решения
        self.task_results[decision_id] = {
            'status': 'success',
            'result': result,
            'condition': condition
        }

    def evaluate_decision(self, decision_point: Dict, condition: str) -> bool:
        """
        Evaluate the decision logic at the decision point.
        """
        logger.info(f"Evaluating condition: {condition}")
        
        if not condition:
            return True
            
        try:
            # Создаем локальный контекст для оценки условия
            local_context = {**self.context}
            
            # Безопасная оценка условия
            result = eval(condition, {"__builtins__": {}}, local_context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {str(e)}", exc_info=True)
            return False
        
    def _save_result(self, execution_id: str, timestamp: str, status: str, data: Dict):
        """
        Save the execution result to a file.
        """
        result = {
            'id': execution_id,
            'workflow_id': self.workflow_id,
            'timestamp': timestamp,
            'status': status,
            'data': data
        }
        
        # Добавляем результат в список результатов
        self.results.append(result)
        
        # Создаем директорию для результатов, если она не существует
        results_dir = f"workflows/{self.workflow_id}/results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Сохраняем результат в файл
        result_file = f"{results_dir}/{execution_id}.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        logger.info(f"Saved execution result to {result_file}")
        return result
