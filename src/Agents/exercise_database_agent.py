import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class ExerciseDatabaseAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Exercise Database Agent.
            """
    
        goal = """
            Recommend exercises from your database for the conditioning coach to design a workout routine. 
            """

        backstory = """
            You are an expert in exercise science. You manage a large database of exercises. You give science-based
            recommendations tailored to the individual's goals. 
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def recommend_exercises(self, age: str = '21'):   # Need to add to run_crewai.py
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Recommend exercises for the condition coach agent based on sport, fitness level, and goals.
                If no age is provided in the profile, assume the athlete's age is {age}.

                The program should include:  
                - **Warm-Up & Mobility**: Dynamic stretching, activation drills, and movement prep for sport-specific readiness.  
                - **Strength & Power Development**: Sport-relevant resistance training, plyometrics, and core stabilization exercises.  
                - **Speed, Agility & Endurance**: Acceleration drills, agility ladders, lateral quickness training, and HIIT conditioning.  
                - **Sport-Specific Skill Work**: Movement patterns directly related to the athlete’s sport (e.g., cutting drills for soccer, jump mechanics for basketball).  
                - **Recovery & Injury Prevention**: Flexibility routines, mobility work, prehab exercises, and proper cooldown strategies.  

                Ensure exercises are **personalized based on the athlete’s sport, skill level, and training goals**, 
                with a structured **progression plan** for continuous improvement.  
                
            """),
            agent=self,
            expected_output="An age-appropriate bulleted list of exercises."
        )        