import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile


class BiomechanicsCoachAgent(BaseAgent):
    def __init__(self, player_profile: AthleteProfile, **kwargs):
        name = "Dr. Alex Thompson - Biomechanics Expert"
        pp = player_profile.get_player_profile()  # Abbreviate dictionary access
        print("Player profile: ", pp)
        
        role = f"""
            You are the {pp['primary_sport']} Biomechanics Coach Agent who also knows about {pp['secondary_sport']}, responsible for analyzing 
                the player's biomechanical performance based on structured input data. 
                
            You provide expert feedback to optimize movement efficiency and prevent injuries.
            """
    
        goal = f"""
            Analyze the player profile of {pp['athlete_name']}. They are a {pp['athlete_age']} year old {pp['sex']}.
            They have a unique aspect of {pp['unique_aspect']} whose primary sport is {pp['primary_sport']} and 
                whose secondary sport is {pp['secondary_sport']}.
            
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
            **kwargs
        )

        self.player_profile = player_profile


    def analyze_biometrics(self):
        return crewai.Task(
            description=dedent(f"""
                Analyze the following athlete profile data and generate a biomechanics assessment:
                               {self.player_profile.get_player_profile()}   

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

