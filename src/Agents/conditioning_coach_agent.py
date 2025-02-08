import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class ConditioningCoachAgent(BaseAgent):
    role: str
    goal: str
    backstory: str
    input_file: str  

    def __init__(self, input_file: str, **kwargs):
        role = """
            You are the Conditioning Coach, responsible for designing and managing athletic training programs.
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
            input_file=input_file,
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

    def create_conditioning_program(self):
        """ Reads the input file and generates a personalized conditioning program """
        player_data = self.read_input_file()  

        return crewai.Task(
            description=dedent(f"""
                Using the provided player data, design a personalized conditioning program 
                that enhances performance while preventing injuries.

                Player Data:
                {player_data}

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
