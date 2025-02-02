##################### Biomechanics Coach Guide #########################
import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class BiomechanicsCoachAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the BiomechanicsCoachAgent
            """
    
        goal = """
            provide feedback to players on their technique.
            The purpose of this feedback is to help correct biomechanical errors
            and prevent injury all while enhancing athletic performance.
            """

        backstory = """
            You are an expert in biomechanics with decades of experience.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def analyze_biometrics(self):
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Given data in the knowledge folder, assess the player's biometrics.
            """),
            agent=self,
            expected_output="An assessment report on biometrics and what needs to be improved"
        )


