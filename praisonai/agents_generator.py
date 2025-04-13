# Import necessary libraries
import os
import json
import uuid
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentsGenerator")

def generate_agent(data, name=None, role=None, abilities=None):
    """Generate an agent based on the provided data, including name, role, and abilities."""
    agent = {
        "id": str(uuid.uuid4()),
        "name": name,
        "role": role,
        "abilities": abilities,
        "data": data
    }
    logger.info(f"Generated agent with ID: {agent['id']}")
    # Logic to generate agent
    logger.info(f"Generated agent with ID: {agent_id}")
    return agent_id

def save_agent(agent_id, agent_data):
    """Save the generated agent data, including versioning."""
    agent_data['version'] = "1.0"  # Adding versioning to the agent data
    try:
        os.makedirs("agents", exist_ok=True)
        with open(f"agents/{agent_id}.json", "w") as f:
            json.dump(agent_data, f, indent=2)
        logger.info(f"Agent {agent_id} saved successfully.")
    except Exception as e:
        logger.error(f"Error saving agent {agent_id}: {str(e)}")

def load_agent(agent_id):
    """Load an agent's data and validate its structure."""
    agent_data = None
    try:
        with open(f"agents/{agent_id}.json", "r") as f:
            agent_data = json.load(f)
        if not isinstance(agent_data, dict) or 'id' not in agent_data:
            logger.error(f"Invalid structure for agent {agent_id}.")
            return None
        logger.info(f"Loaded agent {agent_id} successfully with data: {agent_data}")
        return agent_data
    except FileNotFoundError:
        logger.error(f"Agent {agent_id} not found.")
        return None
    except Exception as e:
        logger.error(f"Error loading agent {agent_id}: {str(e)}")
        return None
