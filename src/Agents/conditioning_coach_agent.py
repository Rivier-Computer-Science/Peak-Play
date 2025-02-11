import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class ConditioningCoachAgent(BaseAgent):
    def __init__(self, **kwargs):
        name = "Coach Mike Reynolds - Strength & Conditioning"
        role = """
            You are the Conditioning Coach Agent, responsible for designing and managing athletic training programs.
            Your expertise ensures athletes develop strength, endurance, and injury resilience.
            You will analyze player-specific data from an input file to create personalized workout plans.
            """
    
        goal = """
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

    def create_conditioning_program(self):
        return crewai.Task(
            description=dedent(f"""
                Using the provided player data, design a personalized conditioning program 
                that enhances performance while preventing injuries.

                Use knowledge in the Crew's context               

                The program should include:
                - Strength training (targeting key muscle groups)
                - Endurance workouts (intervals, stamina-building routines)
                - Flexibility and mobility exercises
                - Recovery protocols (rest, nutrition, injury prevention)
                - Weekly progression plans
            """),
            agent=self,
            expected_output="A structured 1-month conditioning plan with weekly adjustments."
        )
    
    def modify_training_program(self):
        return crewai.Task(
            description=dedent(f"""
                Analyze updated player performance data and adjust the training plan accordingly.

                Adaptations should include:
                - Increasing intensity if performance is improving.
                - Reducing intensity if signs of fatigue or overtraining appear.
                - Modifying exercises based on weaknesses or injury risks.
                - Updating recovery strategies if necessary.

                The goal is to ensure **continuous improvement** while preventing injuries.
            """),
            agent=self,
            expected_output="An updated training plan reflecting new performance insights."
        )
