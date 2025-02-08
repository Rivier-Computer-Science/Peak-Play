import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class NutritionAgent(BaseAgent):
    role: str
    goal: str
    backstory: str
    input_file: str  

    def __init__(self, input_file: str, **kwargs):
        role = """
            You are a Sports Nutrition Coach specializing in optimizing athlete performance through diet.
            Your role is to **analyze player-specific data** and design **customized meal plans** 
            that enhance energy, endurance, recovery, and overall health.
            """
    
        goal = """
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
            input_file=input_file,
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

    def generate_meal_plan(self):
        """ Reads the input file and generates a personalized meal plan """
        player_data = self.read_input_file()  # Fetch player profile dynamically

        return crewai.Task(
            description=dedent(f"""
                Read the following player profile and create a **customized 1-month meal plan**:

                **Player Data:**
                {player_data}

                The meal plan should:
                - Be **tailored to the athlete’s specific training** and performance needs.
                - Include **high-protein meals** for muscle recovery.
                - Optimize **carbohydrate intake** for energy levels.
                - Balance **fats, vitamins, and hydration** for overall health.
                - Incorporate **pre-game and post-game nutrition strategies**.
                - Recommend **meal timing and portion sizes**.

                Ensure the plan **enhances endurance, strength, and recovery**, while preventing fatigue and injury.
            """),
            agent=self,
            expected_output="A structured 1-month meal plan designed to optimize the athlete’s performance."
        )
