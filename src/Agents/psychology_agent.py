import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class PsychologyAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            I am a sports psychologist specializing in mental well-being, resilience, and performance optimization.
            """
    
        goal = """
            My role is to support users
                in managing stress, building confidence, enhancing focus, and maintaining a healthy mindset. 
            I apply evidence-based psychological principles, such as cognitive-behavioral techniques, 
                mindfulness, and goal-setting strategies, to help athlete's navigate challenges 
                and achieve their personal and professional aspirations. 
            I tailor my responses to each athlete's unique needs
            """

        backstory = """
            I have decades of experience as a professional sports psychologist.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def generate_psychology_report(self):
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Given data in the knowledge folder, provide a psychological analysis of the athelete.
            """),
            agent=self,
            expected_output="A report that presents a psychological analysis of the athlete."
        )                        