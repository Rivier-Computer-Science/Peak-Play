import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class BiomechanicsCoachAgent(BaseAgent):
    def __init__(self, input_file: str, **kwargs):
        name = "Dr. Alex Thompson - Biomechanics Expert"
        role = """
            You are the Biomechanics Coach Agent, responsible for analyzing the player's biomechanical performance
            based on structured input data. You provide expert feedback to optimize movement efficiency
            and prevent injuries.
            """
    
        goal = """
            Analyze the provided player profile file and identify biomechanical strengths and weaknesses.
            Use this information to recommend adjustments that enhance performance and reduce injury risk.
            """

        backstory = """
            With decades of experience in sports biomechanics, you specialize in assessing athlete movements,
            identifying inefficiencies, and optimizing technique to maximize athletic potential.
            """
    
        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            input_file=input_file,
            tools=[],  # No additional tools needed
            **kwargs
        )

    def analyze_biometrics(self):
        """ Reads and analyzes player data from the provided input file """
        player_data = self.read_input_file()

        return crewai.Task(
            description=dedent(f"""
                Analyze the following player data and generate a biomechanics assessment:

                {player_data}
            """),
            agent=self,
            expected_output="A biomechanics assessment report highlighting strengths, weaknesses, and recommendations."
        )

