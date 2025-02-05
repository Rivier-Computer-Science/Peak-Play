import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class ConditioningCoachAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the ConditioningCoachAgent
            """
    
        goal = """
            develop and manage training programs for athletes. 
            Design workout routines, track progress, and adjust plans based on performance 
            and user feedback.
            """

        backstory = """
            You are an expert in fitness and conditioning with decades of experience.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def create_conditioning_program(self):  # Need to add to run_crewai.py
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Given data in the knowledge folder, create a conditioning program.
            """),
            agent=self,
            expected_output="A daily plan for 1 month with a conditioning routine."
        )        
    def modify_training_plan(self):  # Need to add to run_crewai.py
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Based on feedback from the user, you are to dynamically update your previously prescribed
                training plan. Update exercise selection, reps, number of sets as needed.
            """),
            agent=self,
            expected_output="An updated daily plan for one month.",
            context=["create_conditioning_program"]
        )        