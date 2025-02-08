from fastapi import FastAPI
from dotenv import load_dotenv
import os
import crewai as crewai
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent

# RUN LOCALLY
# uvicorn app:app --host 0.0.0.0 --port 8000

# Load environment variables
load_dotenv("/etc/secrets")

# Initialize FastAPI app
app = FastAPI()

class AssessmentCrew:
    def __init__(self):
        self.is_init = True

    def run(self):
        player_profile = TextFileKnowledgeSource(file_paths=["player_profile.txt"])

        # Initialize agents
        biomechanics_coach_agent = BiomechanicsCoachAgent()
        conditioning_coach_agent = ConditioningCoachAgent()
        motivator_agent = MotivatorAgent()
        nutrition_agent = NutritionAgent()
        physiology_agent = PhysiologyAgent()
        position_coach_agent = PositionCoachAgent()
        psychology_agent = PsychologyAgent()

        agents = [
            biomechanics_coach_agent, 
            conditioning_coach_agent,
            motivator_agent,
            nutrition_agent,
            physiology_agent,
            position_coach_agent,
            psychology_agent,
        ]

        tasks = [
            biomechanics_coach_agent.analyze_biometrics(),
            conditioning_coach_agent.create_conditioning_program(),
            motivator_agent.motivate_athelete(),
            nutrition_agent.generate_meal_plan(),
            physiology_agent.generate_physiology_report(),
            position_coach_agent.generate_position_advice(),
            psychology_agent.generate_psychology_report()
        ]
    
        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            knowledge_sources=[player_profile],
            process=crewai.Process.sequential,
            verbose=False
        )

        result = crew.kickoff()
        return result

@app.post("/run_assessment")
def run_assessment():
    assessment_crew = AssessmentCrew()
    try:
        crew_output = assessment_crew.run()
        return {"success": True, "crew_output": crew_output}
    except Exception as e:
        return {"success": False, "error": str(e)}
