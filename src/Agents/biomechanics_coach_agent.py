import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile


class BiomechanicsCoachAgent(BaseAgent):
    def __init__(self, athlete_profile: AthleteProfile, **kwargs):
        name = "Dr. Alex Thompson - Biomechanics Expert"
        ap = athlete_profile.get_athlete_profile()  # Abbreviate dictionary access
        #print("Player profile: ", ap)
        
        role = f"""
            You are the {ap['primary_sport']} Biomechanics Coach Agent who also knows about {ap['secondary_sport']}, responsible for analyzing 
                the player's biomechanical performance based on structured input data. 
                
            You provide expert feedback to optimize movement efficiency and prevent injuries.
            """
    
        goal = f"""
            Analyze the player profile of {ap['athlete_name']}. They are a {ap['athlete_age']} year old {ap['sex']}.
            They have a unique aspect of {ap['unique_aspect']} whose primary sport is {ap['primary_sport']} and 
                whose secondary sport is {ap['secondary_sport']}.
            
            Identify biomechanical strengths and weaknesses.
            Use this information to recommend adjustments that enhance performance and reduce injury risk.
            """

        backstory = """
            With decades of experience in sports biomechanics, you specialize in assessing athlete movements,
            identifying inefficiencies, and optimizing technique to maximize athletic potential.
            This knowledge base ensures that the 
            biomechanics assessments and recommendations are tailored to each athlete’s individual needs.
            """
        
        super().__init__(athlete_profile=athlete_profile,
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),                   
            **kwargs
        )

    def analyze_biometrics(self):
        ap = self.athlete_profile.get_athlete_profile()  #get athlete profile data
        return crewai.Task(
            description=dedent(f"""
                Analyze the following athlete profile data and generate a biomechanics assessment:  

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
            expected_output="An age-appropriate biomechanics assessment report highlighting strengths, weaknesses, and recommendations. Do not include the athlete profile data in the output."
            
        )

