import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class FitbitAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Analyst Agent.
            """
    
        goal = """
            Analyze user data from the form provided in the context provide to the Crew to update training program.
            """

        backstory = """
            As an expert analyst, you have a long history of working in the field of exercise science. You are there
            to analyze the provided data so that the other agents can optimize the user's training program.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def analyze_data(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Analyze the feedback from the user and summarize/distill important imformation for the other agents to provide
                personalized recommendations to the user's training program.
            """),
            agent=self,
            expected_output="Summary of key data points. Analysis of data."
        )        