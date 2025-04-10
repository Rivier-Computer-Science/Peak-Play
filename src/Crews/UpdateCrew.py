import crewai

from src.Helpers.athlete_profile import AthleteProfile

# Import Agents
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent

class UpdateCrew:
    def __init__(self, player_data):
        self.athlete_data = AthleteProfile(player_data)

    def run(self, task_id: str):
        # Initialize agents with file input
        conditioning_coach_agent = ConditioningCoachAgent(athlete_profile=self.athlete_data)
        motivator_agent = MotivatorAgent(athlete_profile=self.athlete_data)
        nutrition_agent = NutritionAgent(athlete_profile=self.athlete_data)
        physiology_agent = PhysiologyAgent(athlete_profile=self.athlete_data)

        agents = [
            conditioning_coach_agent,
            motivator_agent,
            nutrition_agent,
            physiology_agent
        ]

        tasks = [
            conditioning_coach_agent.modify_training_program(),
            motivator_agent.motivate_athlete(),
            nutrition_agent.generate_meal_plan(),
            physiology_agent.generate_physiology_report(),
        ]
    
        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            process=crewai.Process.sequential,
            verbose=False
        )

        result = crew.kickoff()       
        return result