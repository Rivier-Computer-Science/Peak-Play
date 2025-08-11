import crewai as crewai

from src.Agents.base_agent import BaseAgent


# ---------------------------------------------------------------------
# Base agent with LLM selection
# ---------------------------------------------------------------------
class BlogBaseAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, llm: crewai.LLM, **kwargs):
        # Extract required parameters
        role : str = kwargs.pop('role', None)
        goal : str = kwargs.pop('goal', None)
        backstory: str = kwargs.pop('backstory', None)        
        kwargs.pop('llm', None)  #Remove it from kwargs if it is there
        llm = llm

        # Ensure required arguments are provided
        if role is None or goal is None or backstory is None:
            raise ValueError(
                f"Error: Missing one of ['role', 'goal', 'backstory']. "
                f"Received: role={role}, goal={goal}, backstory={backstory}"
            )

        super().__init__(
            name=kwargs.pop('name', None),
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
        )

