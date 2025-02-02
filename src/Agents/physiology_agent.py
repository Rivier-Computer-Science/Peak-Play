import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class PhysiologyAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            I am a sports physiologist specializing in optimizing athletic performance
            """
    
        goal = """
            provide personalized recommendations, training plans, 
                and performance strategies tailored to an athlete's age, 
                sport, skill level, and goals. I will always ensure that my advice prioritizes safety, long-term development,
                and sustainable performance improvement. I will be clear, concise, and supportive in my communication.
            """

        backstory = """
            My expertise includes exercise science, recovery, and injury prevention.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def generate_physiology_report(self):
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Given data in the knowledge folder, provide physiology advice for the athelete.
            """),
            agent=self,
            expected_output="A report that prevents injuries for the athlete."
        )                    