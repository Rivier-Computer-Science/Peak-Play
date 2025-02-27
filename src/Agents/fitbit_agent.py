import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class FitbitAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Analyst Agent.
            """
    
        goal = """
            Analyze user data from the form provided in the context provide to the Crew to update training program.
            """

        backstory = """
            As an expert analyst, you have a long history of working in the field of exercise science. You are there
            to analyze the provided data so that the other agents can optimize the user's training program.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def analyze_data(self, age: str = '21'): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Analyze the feedback from the user and summarize/distill important information for the other agents to provide
                personalized recommendations to the user's training program.
                If no age is provided in the profile, assume the athlete's age is {age}.

                **The summary report should include:**
                - **Performance Trends**: Identify strengths, weaknesses, and improvements over time.  
                - **Biomechanical Analysis**: Highlight movement inefficiencies, imbalances, and injury risks.  
                - **Training Effectiveness**: Assess the impact of workouts on performance metrics.  
                - **Nutritional Insights**: Summarize dietary habits and potential adjustments for better recovery and energy.  
                - **Recovery & Readiness**: Evaluate fatigue levels, sleep quality, and overall recovery status.  
                - **Personalized Recommendations**: Provide actionable insights for training, conditioning, and nutrition.  

                Ensure the analysis is **concise, data-driven, and tailored** to the athlete's sport and goals.  

            """),
            agent=self,
            expected_output="An age-appropriate summary of key data points and analysis of data."
        )        