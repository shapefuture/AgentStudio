# tests/test_agents_playbook.py
import unittest
# from unittest.mock import patch
from praisonai.agents_generator import generate_agent, save_agent, load_agent

class TestPraisonAIFramework(unittest.TestCase):    
    def test_generate_agent(self):
        agent_id = generate_agent(data="Sample data", name="Test Agent", role="Researcher", abilities=["Analyze", "Research"])
        self.assertIsNotNone(agent_id)

    def test_save_agent(self):
        agent_data = {
            "id": "test-id",
            "name": "Test Agent",
            "role": "Researcher",
            "abilities": ["Analyze", "Research"],
            "data": "Sample data",
            "version": "1.0"
        }
        save_agent(agent_id="test-id", agent_data=agent_data)

    def test_load_agent(self):
        loaded_agent = load_agent(agent_id="test-id")
        self.assertIsNotNone(loaded_agent)
        self.assertEqual(loaded_agent['name'], "Test Agent")
    # def test_main_with_autogen_framework(self):
        praisonai = PraisonAI(agent_file='tests/autogen-agents.yaml')
        result = praisonai.run()
        self.assertIn('### Task Output ###', result)

    # def test_main_with_custom_framework(self):
        praisonai = PraisonAI(agent_file='tests/crewai-agents.yaml')
        result = praisonai.run()
        self.assertIn('### Task Output ###', result)

    # def test_main_with_internet_search_tool(self):
        praisonai = PraisonAI(agent_file='tests/search-tool-agents.yaml')
        result = praisonai.run()
        self.assertIn('### Task Output ###', result)

    # def test_main_with_built_in_tool(self):
        praisonai = PraisonAI(agent_file='tests/inbuilt-tool-agents.yaml')
        result = praisonai.run()
        self.assertIn('### Task Output ###', result)
