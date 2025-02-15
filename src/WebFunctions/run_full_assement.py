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

class RunFullAssessmentCrew:
    def __init__(self, player_data: str):
        self.player_data = StringKnowledgeSource(content=player_data)

    def run(self, task_id: str):
        # Initialize agents with file input
        biomechanics_coach_agent = BiomechanicsCoachAgent()
        conditioning_coach_agent = ConditioningCoachAgent()
        motivator_agent = MotivatorAgent()
        nutrition_agent = NutritionAgent()
        physiology_agent = PhysiologyAgent()
        position_coach_agent = PositionCoachAgent()
        psychology_agent = PsychologyAgent()
        comprehensive_report_agent = ComprehensiveReportAgent()

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
            knowledge_sources=[self.player_data],
            process=crewai.Process.sequential,
            verbose=False
        )

        result = crew.kickoff()       
        return result