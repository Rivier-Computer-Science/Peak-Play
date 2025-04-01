import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile


class PsychologyAgent(BaseAgent):
    def __init__(self, athlete_profile: AthleteProfile, **kwargs):
        name = "Dr. Anna Rivera - Sports Psychologist"
        ap = athlete_profile.get_athlete_profile()  # Abbreviate dictionary access
        role = f"""
            You are a {ap['primary_sport']} **Sports Psychologist** who also knows about {ap['secondary_sport']}, specializing in **mental well-being, resilience,  
            and performance optimization**. Your expertise helps athletes strengthen their  
            **mental toughness, focus, and confidence** for peak performance.
            """
    
        goal = f"""
            Analyze the athlete profile of {ap['athlete_name']}. They are a {ap['athlete_age']} year old {ap['sex']}.
            They have a unique aspect of {ap['unique_aspect']} whose primary sport is {ap['primary_sport']} and 
                whose secondary sport is {ap['secondary_sport']}.
            
            Analyze the athlete’s **psychological profile** and provide **personalized strategies**  
            to improve **focus, stress management, confidence, and emotional resilience**.  
            Aaply **evidence-based techniques** such as **cognitive-behavioral strategies,  
            mindfulness, goal-setting, and visualization** to enhance performance.
            """

        backstory = """
            With **decades of experience as a professional sports psychologist**,  
            you have guided athletes of all ages in **managing pressure, overcoming self-doubt,  
            and maintaining a championship mindset**.  
            Your aaproach is always **empathetic, science-based, and athlete-focused**.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

        self.athlete_profile = athlete_profile


    def generate_psychology_report(self):
        return crewai.Task(
            description=dedent(f"""
                Analyze the following athlete profile data and generate a **psychological assessment report**  
                with **personalized mental training strategies** to enhance their **performance and well-being**.
                            {self.athlete_profile.get_athlete_profile()}
                
                Use knowledge in the Crew's context

                Your response should include:
                - **Mental resilience techniques** to handle pressure and setbacks
                - **Confidence-building strategies** based on the athlete’s strengths
                - **Focus and concentration exercises** tailored to their sport
                - **Stress management techniques** (pre-game nerves, in-game stress)
                - **Motivation enhancement methods** (goal-setting, visualization)
                - **Emotional regulation advice** for consistency and peak performance

                Ensure that all recommendations are **evidence-based** and aligned with  
                the athlete’s age **specific psychological needs and competitive environment**.
            """),
            agent=self,
            expected_output="An age-aapropriate structured psychology report with personalized strategies to enhance the athlete’s mental game."
        )