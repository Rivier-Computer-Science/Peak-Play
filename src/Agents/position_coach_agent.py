import crewai as crewai
from textwrap import dedent
import json
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile

class PositionCoachAgent(BaseAgent):
    def __init__(self, player_profile: AthleteProfile, **kwargs):
        name = "Coach Daniel Morgan - Positional Specialist"
        pp = player_profile.get_player_profile()  # Abbreviate dictionary access
        role = f"""
            You are a {pp['primary_sport']} **Position Coach** who also knows about {pp['secondary_sport']}, specializing in coaching techniques specific to an athlete’s  
            field position. You analyze **player data** to provide **targeted skill development strategies**  
            that enhance performance in their role.
            """
    
        goal = f"""
            Analyze the player profile of {pp['athlete_name']}. They are a {pp['athlete_age']} year old {pp['sex']}.
            They have a unique aspect of {pp['unique_aspect']} whose primary sport is {pp['primary_sport']} and 
                whose secondary sport is {pp['secondary_sport']}.
            
            Provide **personalized coaching advice** based on the athlete’s **position, strengths, and areas for improvement**.  
            Develop **position-specific drills, techniques, and strategic insights** that refine skills and improve decision-making.
            """

        backstory = """
            With extensive experience coaching athletes in **specialized field positions**,  
            you understand the **technical, tactical, and mental aspects** required for excellence.  
            Your training methods are backed by **sports science and real-game scenarios**.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

        self.player_profile = player_profile

    def generate_position_advice(self):
        return crewai.Task(
            description=dedent(f"""
                Read the following player profile and generate **customized position coaching advice**  
                to enhance their **on-field performance, skill execution, and game awareness**.
                            {self.player_profile.get_player_profile()}

                Use knowledge in the Crew's context

                Your response should include:
                - **Technical adjustments** specific to their **position**
                - **Drills and training methods** that refine **position-specific skills**
                - **Game strategies** to improve decision-making and situational awareness
                - **Tactical advice** based on **real-game scenarios**
                - **Corrective feedback** on common **positional weaknesses**
                
                Ensure that all recommendations are **evidence-based** and aligned with
                the athlete’s age **specific skill level and long-term development**.
            """),
            agent=self,
            expected_output="An age-appropriate structured coaching report tailored to the athlete’s position."
        )
