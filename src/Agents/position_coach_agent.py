import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class PositionCoachAgent(BaseAgent):
    def __init__(self, **kwargs):
        name = "Coach Daniel Morgan - Positional Specialist"
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
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

    def generate_position_advice(self, age: str = '21'):
        return crewai.Task(
            description=dedent(f"""
                Read the following player profile and generate **customized position coaching advice**  
                to enhance their **on-field performance, skill execution, and game awareness**.
                If no age is provided in the profile, assume the athlete's age is {age}.

                Use knowledge in the Crew's context

                Your response should include:
                - **Technical adjustments** specific to their **position**
                - **Drills and training methods** that refine **position-specific skills**
                - **Game strategies** to improve decision-making and situational awareness
                - **Tactical advice** based on **real-game scenarios**
                - **Corrective feedback** on common **positional weaknesses**
                
                Ensure that all recommendations are **evidence-based** and aligned with
                the athlete’s age **specific skill level and long-term development**.
            """),
            agent=self,
            expected_output="An age-appropriate structured coaching report tailored to the athlete’s position."
        )
