from praisonai import PraisonAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Initialize the research analyst agent
    agent = PraisonAI(
        agents_config="docs/agents/research-analyst.mdx",
        framework="praisonai"
    )

    # Execute research workflow
    result = agent.start({
        "urls": [
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://www.ibm.com/topics/artificial-intelligence"
        ],
        "topic": "Latest advancements in AI"
    })

    print("\nResearch Results:")
    print(f"Report ID: {result['report_id']}")
    print(f"Analysis: {result['analysis'][:200]}...")  # Print first 200 chars

if __name__ == "__main__":
    main()
