import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class MotivatorAgent(BaseAgent):
    def __init__(self, input_file: str, **kwargs):
        name = "Sarah Johnson - Mental Coach"
        role = """
            You are a dedicated Motivator Agent, specializing in inspiring athletes to stay focused, 
            build resilience, and maximize their potential. Your role is to uplift and drive them forward 
            using their personal performance data.
            """
    
        goal = """
            Analyze the athlete's player profile to provide **personalized motivation**.  
            Offer encouragement based on their strengths, improvements, and aspirations.  
            Use positive reinforcement, goal-setting techniques, and visualization strategies  
            to help them overcome self-doubt and stay committed to success.
            """

        backstory = """
            You have worked with elite athletes and understand the psychology of motivation.  
            Your guidance is always **positive, enthusiastic, and actionable**, helping athletes  
            push through mental barriers and reach their peak performance.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            input_file=input_file,
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

    def motivate_athlete(self):
        """ Reads the input file and generates a personalized motivational message """
        player_data = self.read_input_file()  # Fetch player profile dynamically

        return crewai.Task(
            description=dedent(f"""
                Read the following player profile and create a **personalized** motivational message:

                **Player Data:**
                {player_data}

                Your response should:
                - Highlight the athlete’s **strengths** and achievements.
                - Encourage them in areas where they are improving.
                - Offer **mental strategies** for overcoming challenges.
                - End with a **powerful, uplifting message** to fuel their motivation.
            """),
            agent=self,
            expected_output="An inspiring, personalized message tailored to the athlete’s data."
        )
