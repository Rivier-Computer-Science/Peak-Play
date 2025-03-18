import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class BiomechanicsCoachAgent(BaseAgent):
    def __init__(self, **kwargs):
        name = "Dr. Alex Thompson - Biomechanics Expert"
        role = f"""
            You are the {self.primary_sport} Biomechanics Coach Agent who also knows about {self.secondary_sport}, responsible for analyzing the player's biomechanical performance
            based on structured input data. You provide expert feedback to optimize movement efficiency
            and prevent injuries.
            """
    
        goal = f"""
            Analyze the player profile of {self.athlete_name}. They are a {self.athlete_age} year old {self.sex}.
            They have a unique aspect of {self.unique_aspect} and play {self.primary_sport} and {self.secondary_sport}.
            
            Identify biomechanical strengths and weaknesses.
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
            tools=[],  # No additional tools needed
            **kwargs
        )


    def analyze_biometrics(self):
        return crewai.Task(
            description=dedent(f"""
                Analyze the following player data and generate a biomechanics assessment:
                If no age is provided in the profile, assume the athlete's age is {self.athlete_age}.

                Use knowledge in the Crew's context

                The biomechanics assessment should include:
                - **Movement Efficiency**: Evaluate mobility, balance, and joint alignment.
                - **Asymmetry & Imbalances**: Identify left vs. right-side discrepancies.
                - **Force & Load Distribution**: Assess stress on joints and risk of overuse injuries.
                - **Sport-Specific Mechanics**: Analyze movement patterns relevant to the athlete’s sport.
                - **Injury Risk Factors**: Highlight potential weaknesses and instability.
                - **Recommendations**: Provide corrective exercises and technique improvements.

                Ensure that all recommendations are *evidence-based** and aligned with  
                the athlete’s age **specific biomechanic needs and competitive environment**.


            """),
            agent=self,
            expected_output="An age-appropriate biomechanics assessment report highlighting strengths, weaknesses, and recommendations."
        )

