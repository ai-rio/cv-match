"""Agent Manager for LLM services in the CV-Match backend."""

class AgentManager:
    """Manages LLM agents for various tasks."""
    
    def __init__(self):
        """Initialize the agent manager."""
        self.agents = {}
    
    def get_agent(self, agent_type: str):
        """Get an agent by type."""
        return self.agents.get(agent_type)
    
    def register_agent(self, agent_type: str, agent):
        """Register an agent."""
        self.agents[agent_type] = agent