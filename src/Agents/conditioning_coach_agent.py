import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile


class ConditioningCoachAgent(BaseAgent):
    def __init__(self, player_profile: AthleteProfile, **kwargs):
        name = "Coach Mike Reynolds - Strength & Conditioning"
        pp = player_profile.get_player_profile()  # Abbreviate dictionary access
        role = f"""
            You are the {pp['primary_sport']} Conditioning Coach Agent who also knows about {pp['secondary_sport']}, responsible for designing and managing athletic training programs.
            Your expertise ensures athletes develop strength, endurance, and injury resilience.
            You will analyze player-specific data from an input file to create personalized workout plans.
            """
    
        goal = f"""

            Analyze the player profile of {pp['athlete_name']}. They are a {pp['athlete_age']} year old {pp['sex']}.
            They have a unique aspect of {pp['unique_aspect']} whose primary sport is {pp['primary_sport']} and 
                whose secondary sport is {pp['secondary_sport']}.

            Use the player's performance data to design a comprehensive conditioning program.
            This program should target strength, endurance, flexibility, and injury prevention.
            Adjust training intensity based on individual fitness levels and game demands.
            """

        backstory = """
            With decades of experience in sports conditioning, you specialize in tailoring 
            training regimens to optimize athletic performance. You have worked with elite 
            athletes across multiple sports, focusing on injury prevention and peak conditioning.
            """

        super().__init__(
            name=kwargs.pop('name', name),            
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

        self.player_profile = player_profile


    def create_conditioning_program(self):
        return crewai.Task(
            description=dedent(f"""                 
                Analyze the following athlete profile data and generate a conditioning program:
                               {self.player_profile.get_player_profile()}  

                Using the provided player data, design a personalized conditioning program 
                that enhances performance while preventing injuries.
                If no age is provided in the profile, assume the athlete's age is {self.athlete_age}.

                Use knowledge in the Crew's context               

                The program should include:
                - Strength training (targeting key muscle groups)
                - Endurance workouts (intervals, stamina-building routines)
                - Flexibility and mobility exercises
                - Recovery protocols (rest, nutrition, injury prevention)
                - Weekly progression plans

                Ensure the program is aligned with the athlete's age, **sport-specific**, and **goal-oriented**.

            """),
            agent=self,
            expected_output="An age-appropriate structured 1-month conditioning plan with weekly adjustments."
        )
    
    def modify_training_program(self, age: str = '21'):
        return crewai.Task(
            description=dedent(f"""
                Analyze updated player performance data and adjust the training plan accordingly.
                If no age is provided in the profile, assume the athlete's age is {age}.

                Adaptations should include:
                - Increasing intensity if performance is improving.
                - Reducing intensity if signs of fatigue or overtraining appear.
                - Modifying exercises based on weaknesses or injury risks.
                - Updating recovery strategies if necessary.

                Ensure the program is aligned with the athlete's age, with the goal of **continuous improvement** while preventing injuries.
            """),
            agent=self,
            expected_output="An age-appropriate updated training plan reflecting new performance insights."
        )

    def generate_report(self):
        return crewai.Task(
            description=dedent(f"""
                This agent takes input from a user-submitted form detailing their workout session and generates 
                a concise summary. The report highlights key aspects such as exercises performed, sets and reps, 
                weights used, workout duration, and any notable observations. 
                The goal is to provide a brief yet informative recap of the session without tracking long-term progress.
            """),
            agent=self,
            expected_output="A report summarizing key infomration about a user's training session."
        )
