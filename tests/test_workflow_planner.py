import unittest
from unittest.mock import patch, MagicMock
from praisonai.workflow_planner import WorkflowPlanner
import json

class TestWorkflowPlanner(unittest.TestCase):
    def setUp(self):
        self.project_brief = {
            "project_brief": "Create a startup for AI-powered market research"
        }
        self.planner = WorkflowPlanner(self.project_brief)

    def test_load_agent_templates(self):
        templates = self.planner._load_agent_templates()
        self.assertIsInstance(templates, dict)
        self.assertGreater(len(templates), 0)

    def test_generate_basic_workflow(self):
        workflow = self.planner.generate_basic_workflow()
        self.assertIsInstance(workflow, dict)
        self.assertIn('nodes', workflow)
        self.assertIn('edges', workflow)
        self.assertGreater(len(workflow['nodes']), 0)
        self.assertGreater(len(workflow['edges']), 0)

    def test_analyze_project_brief(self):
        tasks = self.planner.analyze_project_brief()
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)

    def test_determine_workflow(self):
        tasks = self.planner.analyze_project_brief()
        workflow = self.planner.determine_workflow(tasks)
        self.assertIsInstance(workflow, dict)
        self.assertIn('tasks', workflow)
        self.assertGreater(len(workflow['tasks']), 0)

    def test_generate_workflow_json(self):
        tasks = self.planner.analyze_project_brief()
        workflow = self.planner.determine_workflow(tasks)
        workflow_json = self.planner.generate_workflow_json(workflow)
        self.assertIsInstance(workflow_json, dict)
        self.assertIn('nodes', workflow_json)
        self.assertIn('edges', workflow_json)
        self.assertGreater(len(workflow_json['nodes']), 0)
        self.assertGreater(len(workflow_json['edges']), 0)

    @patch('praisonai.workflow_planner.OpenAI')
    def test_plan_workflow_with_llm(self, mock_openai):
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "nodes": [{
                "id": "task1",
                "type": "default",
                "data": {"label": "Task 1", "agent_type": "analyst"},
                "position": {"x": 100, "y": 100}
            }],
            "edges": []
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Test with LLM
        self.planner.llm_client = mock_client
        workflow = self.planner.plan_workflow_with_llm()
        self.assertIsInstance(workflow, dict)
        self.assertIn('nodes', workflow)

    def test_validate_workflow_json(self):
        valid_workflow = {
            "nodes": [{
                "id": "task1",
                "type": "default",
                "data": {"label": "Task 1", "agent_type": "analyst"},
                "position": {"x": 100, "y": 100}
            }],
            "edges": []
        }
        self.assertTrue(self.planner._validate_workflow_json(valid_workflow))

        invalid_workflow = {"nodes": [], "edges": []}
        self.assertFalse(self.planner._validate_workflow_json(invalid_workflow))

if __name__ == '__main__':
    unittest.main()