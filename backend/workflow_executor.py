from langgraph.graph import Graph
from typing import Dict, Any
import logging

class WorkflowExecutor:
    def __init__(self):
        self.active_workflows = {}
        self.logger = logging.getLogger(__name__)

    async def execute_workflow(self, workflow_id: str, workflow_def: Dict[str, Any]):
        """Execute a workflow using LangGraph"""
        try:
            # Validate workflow definition
            if not workflow_def.get('nodes'):
                raise ValueError("Workflow must contain at least one node")
            if not workflow_def.get('entry_point'):
                raise ValueError("Workflow must specify an entry point")

            # Create LangGraph workflow
            workflow = Graph()
            
            # Add nodes from workflow definition
            for node in workflow_def.get('nodes', []):
                if not node.get('id'):
                    raise ValueError("All nodes must have an id")
                
                # Convert string functions to actual callables
                if isinstance(node['function'], str):
                    try:
                        # Wrap the function to handle dict input
                        func_str = node['function']
                        func = eval(f"lambda x: ({func_str})(x)")
                    except Exception as e:
                        raise ValueError(f"Invalid function definition: {str(e)}")
                else:
                    # Wrap raw functions to handle dict input
                    func = lambda x: node['function'](x)
                
                if not callable(func):
                    raise ValueError(f"Node {node['id']} function must be callable")
                
                # Add node with proper state handling
                workflow.add_node(node['id'], lambda state: {
                    'value': func(state['value'] if isinstance(state, dict) and 'value' in state else state),
                    '_prev': state  # Keep previous state for reference
                })
            
            # Add edges from workflow definition  
            for edge in workflow_def.get('edges', []):
                workflow.add_edge(edge['source'], edge['target'])
            
            # Set entry point
            workflow.set_entry_point(workflow_def['entry_point'])
            
            # Execute workflow
            self.active_workflows[workflow_id] = {
                'status': 'running',
                'graph': workflow
            }
            
            # Run the workflow
            app = workflow.compile()
            result = await app.ainvoke(workflow_def.get('input', {}))
            
            self.active_workflows[workflow_id]['status'] = 'completed'
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            self.active_workflows[workflow_id]['status'] = 'failed'
            raise

    def get_workflow_status(self, workflow_id: str):
        """Get status of a running workflow"""
        return self.active_workflows.get(workflow_id, {'status': 'not_found'})
