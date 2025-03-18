import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class PsychologyAgent(BaseAgent):
    def __init__(self, athlete_age: str ='21', **kwargs):
        name = "Dr. Anna Rivera - Sports Psychologist"
        role = """
            You are a **Sports Psychologist**, specializing in **mental well-being, resilience,  
            and performance optimization**. Your expertise helps athletes strengthen their  
            **mental toughness, focus, and confidence** for peak performance.
            """
    
        goal = """
            Analyze the athlete’s **psychological profile** and provide **personalized strategies**  
            to improve **focus, stress management, confidence, and emotional resilience**.  
            Apply **evidence-based techniques** such as **cognitive-behavioral strategies,  
            mindfulness, goal-setting, and visualization** to enhance performance.
            """

        backstory = """
            With **decades of experience as a professional sports psychologist**,  
            you have guided athletes of all ages in **managing pressure, overcoming self-doubt,  
            and maintaining a championship mindset**.  
            Your approach is always **empathetic, science-based, and athlete-focused**.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )


    def generate_psychology_report(self):
        return crewai.Task(
            description=dedent(f"""
                Read the player information in the Crew's context and generate a **psychological assessment report**  
                If no age is provided in the profile, assume the athlete's age is {self.athlete_age}.
                
                Use knowledge in the Crew's context

                Your response should include:
                - **Mental resilience techniques** to handle pressure and setbacks
                - **Confidence-building strategies** based on the athlete’s strengths
                - **Focus and concentration exercises** tailored to their sport
                - **Stress management techniques** (pre-game nerves, in-game stress)
                - **Motivation enhancement methods** (goal-setting, visualization)
                - **Emotional regulation advice** for consistency and peak performance

                Ensure that all recommendations are **evidence-based** and aligned with  
                the athlete’s age **specific psychological needs and competitive environment**.
            """),
            agent=self,
            expected_output="An age-appropriate structured psychology report with personalized strategies to enhance the athlete’s mental game."
        )