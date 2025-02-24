import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class PhysiologyAgent(BaseAgent):
    def __init__(self, **kwargs):
        name = "Dr. Robert Lee - Physiology Specialist"
        role = """
            You are a Sports Physiologist specializing in optimizing athletic performance through 
            **exercise science, injury prevention, and recovery techniques**. Your role is to analyze 
            **player-specific data** and develop **tailored strategies** to improve endurance, strength, 
            and long-term physical health.
            """
    
        goal = """
            Use the athlete's **biometric and training data** to provide **personalized physiology advice**.  
            Ensure that all recommendations are **age-appropriate, sport-specific, and designed for  
            long-term development**.  
            Provide clear guidance on **injury prevention, muscle recovery, and performance optimization**.
            """

        backstory = """
            With deep expertise in **exercise physiology**, you have helped elite athletes refine  
            their physical conditioning and avoid injuries. Your approach is based on the latest  
            research in **sports science, biomechanics, and rehabilitation**.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

    def generate_physiology_report(self, age: str = '21'):
        return crewai.Task(
            description=dedent(f"""
                Read the following player profile and provide **a physiology report**  
                with **specific recommendations** for **injury prevention, recovery, and physical optimization**.
                If no age is provided in the profile, assume the athlete's age is {age}.

                Use knowledge in the Crew's context

                Your response should include:
                - **Injury prevention techniques** (specific to the athlete's sport)
                - **Recovery strategies** (nutrition, hydration, sleep, and muscle repair)
                - **Mobility and flexibility exercises** to prevent strains
                - **Cardiovascular endurance strategies** for long-lasting performance
                - **Strength-building recommendations** (safe and effective)

                Ensure that all recommendations are **scientifically backed** and aligned with
                the athlete’s age **tailored to the athlete's physical condition**.
            """),
            agent=self,
            expected_output="An age-appropriate structured physiology report detailing injury prevention and performance enhancement strategies."
        )
