import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class MotivatorAgent(BaseAgent):
    def __init__(self, athlete_age: str ='21', **kwargs):
        name = "Sarah Johnson - Motivator Coach"
        role = """
            You are a dedicated Motivator Agent, specializing in inspiring athletes to stay focused, 
            build resilience, and maximize their potential. Your role is to uplift and drive them forward 
            using their personal performance data.
            """
    
        goal = """
            Analyze the athlete's player profile in the CrewAI context to provide personalized motivation.  
            Offer encouragement based on their strengths, improvements, and aspirations.  
            Use positive reinforcement, goal-setting techniques, and visualization strategies  
            to help them overcome self-doubt and stay committed to success.
            """

        backstory = """
            You have worked with elite athletes and understand the psychology of motivation.  
            Your guidance is always positive, enthusiastic, and actionable, helping athletes  
            push through mental barriers and reach their peak performance.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

        self.athlete_age = athlete_age

    def motivate_athlete(self):
        return crewai.Task(
            description=dedent(f"""
                Analyze player athlete information in the Crew's context.
                Create a personalized age-specific motivational message:
                
                The athlete's age is {self.athlete_age}.

                Use the knowledge in the Crew's context

                Your response should:
                - Highlight the athlete’s strengths and achievements.
                - Encourage them in areas where they are improving.
                - End with a powerful, uplifting message to encourage them.

                Make sure the motivational message is appropriate to the athlete's age.
            """),
            agent=self,
            expected_output="An age-appropriate inspiring, personalized message tailored to the athlete’s information."
        )
