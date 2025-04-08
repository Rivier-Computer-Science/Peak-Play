import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile

class ExerciseDatabaseAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, athlete_profile: AthleteProfile, **kwargs):
        ap = athlete_profile.get_athlete_profile()  # Abbreviate dictionary access
        role = f"""
            You are the {ap['primary_sport']} Exercise Database Agent who also knows about {ap['secondary_sport']}.

            You provide a comprehensive database of exercises tailored to the athlete's profile.
            """
    
        goal = f"""
            Analyze the player profile of {ap['athlete_name']}. They are a {ap['athlete_age']} year old {ap['sex']}.
            They have a unique aspect of {ap['unique_aspect']} whose primary sport is {ap['primary_sport']} and 
                whose secondary sport is {ap['secondary_sport']}.
            
            Recommend exercises from your database for the conditioning coach to design a workout routine. 
            """

        backstory = """
            You are an expert in exercise science. You manage a large database of exercises. You give science-based
            recommendations tailored to the individual's goals. 
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

        self.athlete_profile = athlete_profile

    def recommend_exercises(self):   # Need to add to run_crewai.py
        ap = self.athlete_profile.get_athlete_profile()  #get athlete profile data
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Recommend exercises for the condition coach agent based on sport, fitness level, and goals.
                Analyze the athlete profile data and recommend exercises.

                The program should include:  
                - **Warm-Up & Mobility**: Dynamic stretching, activation drills, and movement prep for sport-specific readiness.  
                - **Strength & Power Development**: Sport-relevant resistance training, plyometrics, and core stabilization exercises.  
                - **Speed, Agility & Endurance**: Acceleration drills, agility ladders, lateral quickness training, and HIIT conditioning.  
                - **Sport-Specific Skill Work**: Movement patterns directly related to the athlete’s sport (e.g., cutting drills for soccer, jump mechanics for basketball).  
                - **Recovery & Injury Prevention**: Flexibility routines, mobility work, prehab exercises, and proper cooldown strategies.  

                Ensure exercises are **personalized based on the athlete’s sport, skill level, and training goals**, 
                with a structured **progression plan** for continuous improvement.  
                
            """),
            agent=self,
            expected_output="An age-appropriate bulleted list of exercises. Do not include the athlete profile data in the output. Do not include the athlete profile data in the output."
        )        