import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class PositionCoachAgent(BaseAgent):
    role: str
    goal: str
    backstory: str
    input_file: str  

    def __init__(self, input_file: str, **kwargs):
        role = """
            You are a **Position Coach**, specializing in coaching techniques specific to an athlete’s  
            field position. You analyze **player data** to provide **targeted skill development strategies**  
            that enhance performance in their role.
            """
    
        goal = """
            Provide **personalized coaching advice** based on the athlete’s **position, strengths, and areas for improvement**.  
            Develop **position-specific drills, techniques, and strategic insights** that refine skills and improve decision-making.
            """

        backstory = """
            With extensive experience coaching athletes in **specialized field positions**,  
            you understand the **technical, tactical, and mental aspects** required for excellence.  
            Your training methods are backed by **sports science and real-game scenarios**.
            """

        super().__init__(
            input_file=input_file,
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

    def generate_position_advice(self):
        """ Reads the input file and provides position-specific coaching advice """
        player_data = self.read_input_file()  # Fetch player profile dynamically

        return crewai.Task(
            description=dedent(f"""
                Read the following player profile and generate **customized position coaching advice**  
                to enhance their **on-field performance, skill execution, and game awareness**.

                **Player Data:**
                {player_data}

                Your response should include:
                - **Technical adjustments** specific to their **position**
                - **Drills and training methods** that refine **position-specific skills**
                - **Game strategies** to improve decision-making and situational awareness
                - **Tactical advice** based on **real-game scenarios**
                - **Corrective feedback** on common **positional weaknesses**
                
                Ensure that all recommendations align with **the athlete’s skill level and long-term development**.
            """),
            agent=self,
            expected_output="A structured coaching report tailored to the athlete’s position."
        )
