import crewai as crewai
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent
from src.Agents.comprehensive_report_agent import ComprehensiveReportAgent
import src.Agents.agent_helpers as agent_helpers
import src.Utils.utils as utils
from src.Helpers.athlete_profile import AthleteProfile
import json


class RunFullAssessmentCrew:
    def __init__(self, athlete_data):
       # pd = utils.convert_player_profile(athlete_data)
       # self.athlete_data = StringKnowledgeSource(content=pd)
       # print("athlete_data in RunFullAssessment: ", pd)
        
        self.athlete_data = AthleteProfile(athlete_data)
        print("athlete_data in RunFullAssessment: ", self.athlete_data)
        self.player_profile_dict = self.athlete_data.get_athlete_profile()
       #  self.knowledge_source = StringKnowledgeSource(content=json.dumps(self.player_profile_dict))

    def run(self, task_id: str):
        # Initialize agents with file input
        biomechanics_coach_agent = BiomechanicsCoachAgent(athlete_profile=self.athlete_data)
        conditioning_coach_agent = ConditioningCoachAgent(athlete_profile=self.athlete_data)
        motivator_agent = MotivatorAgent(athlete_profile=self.athlete_data)
        nutrition_agent = NutritionAgent(athlete_profile=self.athlete_data)
        physiology_agent = PhysiologyAgent(athlete_profile=self.athlete_data)
        position_coach_agent = PositionCoachAgent(athlete_profile=self.athlete_data)
        psychology_agent = PsychologyAgent(athlete_profile=self.athlete_data)
        comprehensive_report_agent = ComprehensiveReportAgent(athlete_profile=self.athlete_data)

        agents = [
            biomechanics_coach_agent, 
            conditioning_coach_agent,
            motivator_agent,
            nutrition_agent,
            physiology_agent,
            position_coach_agent,
            psychology_agent,
            comprehensive_report_agent,
        ]

        tasks = [
            biomechanics_coach_agent.analyze_biometrics(),
            conditioning_coach_agent.create_conditioning_program(),
            motivator_agent.motivate_athlete(),
            nutrition_agent.generate_meal_plan(),
            physiology_agent.generate_physiology_report(),
            position_coach_agent.generate_position_advice(),
            psychology_agent.generate_psychology_report(),
            comprehensive_report_agent.compile_report()
        ]
    
        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            #task_callback=agent_callback.crewai_callback_task_completion,
            # knowledge_sources=[self.knowledge_source],    
            process=crewai.Process.sequential,
            verbose=True
        )



        result = crew.kickoff()

        return agent_helpers.concatente_task_outputs(result)