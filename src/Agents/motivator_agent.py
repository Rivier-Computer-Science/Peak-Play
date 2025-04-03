import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile

class MotivatorAgent(BaseAgent):
    def __init__(self, athlete_profile: AthleteProfile, **kwargs):
        name = "Sarah Johnson - Motivator Coach"
        ap = athlete_profile.get_athlete_profile()  # Abbreviate dictionary access
        role = f"""
            You are a dedicated {ap['primary_sport']} Motivator Agent who also knows about {ap['secondary_sport']}, specializing in inspiring athletes to stay focused, 
            build resilience, and maximize their potential. Your role is to uplift and drive them forward 
            using their personal performance data.
            """
    
        goal = f"""
            Analyze the player profile of {ap['athlete_name']}. They are a {ap['athlete_age']} year old {ap['sex']}.
            They have a unique aspect of {ap['unique_aspect']} whose primary sport is {ap['primary_sport']} and 
                whose secondary sport is {ap['secondary_sport']}.
            
            Analyze the athlete's player profile in the CrewAI context to provide personalized motivation.  
            Offer encouragement based on their strengths, improvements, and aspirations.  
            Use positive reinforcement, goal-setting techniques, and visualization strategies  
            to help them overcome self-doubt and stay committed to success.
            """

        backstory = """
            You have worked with elite athletes and understand the psychology of motivation.  
            Your guidance is always positive, enthusiastic, and actionable, helping athletes  
            push through mental barriers and reach their peak performance.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

        self.athlete_profile = athlete_profile


    def motivate_athlete(self):
        return crewai.Task(
            description=dedent(f"""
                Analyze the following athlete profile data and create a personalized age-specific motivational message:
                        {self.athlete_profile.get_athlete_profile()}

                Use the knowledge in the Crew's context

                Your response should:
                - Highlight the athlete’s strengths and achievements.
                - Encourage them in areas where they are improving.
                - End with a powerful, uplifting message to encourage them.

                Make sure the motivational message is appropriate to the athlete's age.
            """),
            agent=self,
            expected_output="An age-appropriate inspiring, personalized message tailored to the athlete’s information."
        )
