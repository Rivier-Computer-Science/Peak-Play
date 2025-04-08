import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile


class AthleteProfileAgent(BaseAgent):
    def __init__(self, athlete_profile: AthleteProfile, **kwargs):
        name = ""
        ap = athlete_profile.get_athlete_profile()  # Abbreviate dictionary access
        print("Player profile: ", ap)
        
        role = f"""
            You are the Athlete Profile Agent, responsible for managing and analyzing athlete data. 
            You collect, structure, and provide key insights on the athlete’s profile to ensure personalized training
            and optimal development.
            """
    
        goal = f"""
            Manage the athlete profile for {ap['athlete_name']}, a {ap['athlete_age']} year-old {ap['sex']}.
            They have a unique aspect: {ap['unique_aspect']}. Their primary sport is {ap['primary_sport']}, 
            and they also participate in {ap['secondary_sport']}.
            
            Your objectives:
            - Ensure accurate and structured athlete profile data.
            - Identify key strengths, training history, and areas for improvement.
            - Provide a well-organized athlete profile that supports personalized coaching.
            """

        backstory = """
            With expertise in athlete development, you specialize in managing and analyzing sports profiles. 
            Your role is to track key athlete data, ensure accurate documentation, and provide structured insights 
            to enhance their training experience.
            """
        
        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),                   
            **kwargs
        )

        self.athlete_profile = athlete_profile


    def provide_athlete_profile(self):
        return crewai.Task(
            description=dedent(f"""
                Provide and structure the athlete's profile data:
                               {self.athlete_profile.get_athlete_profile()}   

                **Athlete Information**
                - **Name**: {self.athlete_profile.get_athlete_profile().get('athlete_name')}
                - **Age**: {self.athlete_profile.get_athlete_profile().get('athlete_age')}
                - **Sex**: {self.athlete_profile.get_athlete_profile().get('sex')}
                - **Primary Sport**: {self.athlete_profile.get_athlete_profile().get('primary_sport')}
                - **Secondary Sport**: {self.athlete_profile.get_athlete_profile().get('secondary_sport')}
                - **Unique Trait**: {self.athlete_profile.get_athlete_profile().get('unique_aspect')}

                
                Ensure that data is structured, accurate, organized, and ready for use by AI coaching agents.

            """),
            agent=self,
            expected_output="A structured and well-organized athlete profile for AI coaching agents."
        )

