import unittest
from unittest.mock import patch
from praisonai.agents_generator import generate_agent, save_agent, load_agent

class TestAgentsGenerator(unittest.TestCase):    
    def test_generate_agent(self):
        agent_id = generate_agent(data="Sample data", name="Test Agent", role="Researcher", abilities=["Analyze", "Research"])
        self.assertIsNotNone(agent_id)

    @mock.patch('praisonai.agents_generator.save_agent')
    def test_save_agent(self, mock_save_agent):
        agent_data = {
            "id": "test-id",
            "name": "Test Agent",
            "role": "Researcher",
            "abilities": ["Analyze", "Research"],
            "data": "Sample data",
            "version": "1.0"
        }
        save_agent(agent_id="test-id", agent_data=agent_data)

    @mock.patch('praisonai.agents_generator.load_agent')
    def test_load_agent(self, mock_load_agent):
        loaded_agent = load_agent(agent_id="test-id")
        self.assertIsNotNone(loaded_agent)
        self.assertEqual(loaded_agent['name'], "Test Agent")

if __name__ == '__main__':
    unittest.main()
