import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class NutritionAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            I am the NutritionAgent.
            """
    
        goal = """
            Offer nutrition advice tailored to athletes. 
            Create personalized meal plans, provide dietary tips, and monitor nutritional intake.
            """

        backstory = """
            You are a nutritionist with years of experience working with athelets.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def generate_meal_plan(self):
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Given data in the knowledge folder, provide meal plan for the athelete.
            """),
            agent=self,
            expected_output="A 1 month meal plan that improves the athelete's health."
        )                