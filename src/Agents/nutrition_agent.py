import crewai as crewai
import json
from textwrap import dedent
from src.Agents.base_agent import BaseAgent
from src.Helpers.athlete_profile import AthleteProfile


class NutritionAgent(BaseAgent):
    def __init__(self, athlete_profile: AthleteProfile, **kwargs):
        name = "Dr. Emily Carter - Sports Nutritionist"
        ap = athlete_profile.get_athlete_profile()  # Abbreviate dictionary access

        role = f"""
            You are a {ap['primary_sport']} Sports Nutrition Agent who also knows about {ap['secondary_sport']} specializing in optimizing athlete performance through diet.
            Your role is to **analyze player-specific data** and design **customized meal plans** 
            that enhance energy, endurance, recovery, and overall health.

            You provide expert nutritional guidance to ensure athletes meet their dietary needs.
            """
    
        goal = f"""
            Analyze the player profile of {ap['athlete_name']}. They are a {ap['athlete_age']} year old {ap['sex']}.
            They have a unique aspect of {ap['unique_aspect']} whose primary sport is {ap['primary_sport']} and 
                whose secondary sport is {ap['secondary_sport']}.

            Develop a **personalized nutrition strategy** based on the athlete’s profile.  
            Ensure the meal plan aligns with their **training intensity, recovery needs, and performance goals**.  
            Recommend **specific macronutrient and micronutrient intake** to maximize their athletic output.
            """

        backstory = """
            You are a highly experienced nutritionist who has worked with elite athletes 
            across multiple sports. You **understand the science of sports nutrition**, recovery, and meal 
            timing to ensure peak performance.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

        self.athlete_profile = athlete_profile

    def generate_meal_plan(self):
        ap = self.athlete_profile.get_athlete_profile()  #get athlete profile data
        return crewai.Task(
            description=dedent(f"""
                Read the player profile and create a **customized 1-month meal plan**:

                Use knowledge in the Crew's context

                The meal plan should:
                - Be **tailored to the athlete’s specific training** and performance needs.
                - Meal plan should be **organized by day and include Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday**.
                - Provide meal plan for 4 weeks broken down into 7 days for each week.
                - Include **breakfast, lunch, snack, dinner, pre-workout, and post-workout meals**.
                - Include **high-protein meals** for muscle recovery.
                - Optimize **carbohydrate intake** for energy levels.
                - Balance **fats, vitamins, and hydration** for overall health.
                - Incorporate **pre-game and post-game nutrition strategies**.
                - Recommend **meal timing and portion sizes**.

                Ensure the plan is aligned with the athlete's age and **enhances endurance, strength, and recovery**, while preventing fatigue and injury.
            """),
            agent=self,
            expected_output=dedent(f"""
            \n\n1-MONTH CUSTOMIZED MEAL PLAN FOR {ap['athlete_name']}\n\n
            An age-appropriate structured 1-month meal plan designed to optimize the athlete’s performance. 
            Do not include the athlete profile data in the output."
        """)
        )