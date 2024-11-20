
import os
import json
import logging
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AutoGPT-Orchestrator")

class AgentTask(BaseModel):
    id: str
    description: str
    assigned_agent: Optional[str] = None
    status: str = "pending"
    result: Optional[str] = None

class AgentCapability(BaseModel):
    name: str
    description: str

class AutonomousAgent:
    def __init__(self, agent_id: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.memory = []

    async def execute_task(self, task: AgentTask) -> str:
        logger.info(f"Agent {self.agent_id} executing task: {task.description}")
        # Simulated complex reasoning logic
        await asyncio.sleep(1) 
        result = f"Completed: {task.description} using {self.capabilities[0].name}"
        self.memory.append({"task": task.description, "result": result})
        return result

class Orchestrator:
    def __init__(self, config_path: str):
        self.agents: Dict[str, AutonomousAgent] = {}
        self.tasks: List[AgentTask] = []
        self.load_config(config_path)

    def load_config(self, path: str):
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = json.load(f)
                for agent_data in config.get("agents", []):
                    caps = [AgentCapability(**cap) for cap in agent_data["capabilities"]]
                    self.agents[agent_data["id"]] = AutonomousAgent(agent_data["id"], caps)
        else:
            logger.warning(f"Config file {path} not found. Starting with empty agents.")

    def add_task(self, description: str):
        task_id = f"task-{len(self.tasks) + 1}"
        new_task = AgentTask(id=task_id, description=description)
        self.tasks.append(new_task)
        logger.info(f"Added task: {task_id}")

    async def run(self):
        logger.info("Starting Orchestrator run loop...")
        for task in self.tasks:
            if task.status == "pending":
                # Simple round-robin assignment for demonstration
                agent_id = list(self.agents.keys())[len(self.tasks) % len(self.agents)]
                task.assigned_agent = agent_id
                task.status = "running"
                
                result = await self.agents[agent_id].execute_task(task)
                task.result = result
                task.status = "completed"
                logger.info(f"Task {task.id} completed by {agent_id}")

# Example usage
if __name__ == "__main__":
    # Create a dummy config for demonstration
    dummy_config = {
        "agents": [
            {"id": "researcher-1", "capabilities": [{"name": "web_search", "description": "Search the internet"}]},
            {"id": "writer-1", "capabilities": [{"name": "text_generation", "description": "Write articles"}]}
        ]
    }
    with open("config.json", "w") as f:
        json.dump(dummy_config, f)

    orchestrator = Orchestrator("config.json")
    orchestrator.add_task("Research the latest trends in Generative AI")
    orchestrator.add_task("Summarize the findings into a 500-word report")
    
    asyncio.run(orchestrator.run())
