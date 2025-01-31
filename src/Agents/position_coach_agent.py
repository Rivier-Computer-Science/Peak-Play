import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class PositionCoachAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            I am a sports PositionCoach specializing in coaching advice for the athlete's position
            """
    
        goal = """
            Provide feedback and instruction to players based on their field position.
            Create personalized drills and training plans to refine skills while addressing unique player challenges.
            """

        backstory = """
            I have years of coaching experience in the player's position.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def generate_position_advice(self):
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Given data in the knowledge folder, provide position coaching advice for the athelete.
            """),
            agent=self,
            expected_output="A report that helps the athelete improve their position."
        )                        