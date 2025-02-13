from fastapi import FastAPI, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
import logging
import uuid
import crewai as crewai
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.comprehensive_report_agent import ComprehensiveReportAgent


import src.Utils.utils as utils


PORT = int(os.environ.get("PORT", 8000))  # Default to 8000 for local testing

logger = utils.configure_logger(logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS to allow requests from WordPress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # FIXME: Replace "*" with your WordPress domain after debug
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"], 
    allow_headers=["*"],
)


# Store task results
task_results = {}

class AssessmentInput(BaseModel):
    file_path: str  # WordPress passes file URL or local path

class AssessmentCrew:
    def __init__(self, player_data: str):
        self.player_data = StringKnowledgeSource(content=player_data)

    def run(self, task_id: str):
        # Initialize agents with file input
        conditioning_coach_agent = ConditioningCoachAgent()
        motivator_agent = MotivatorAgent()
        nutrition_agent = NutritionAgent()
        physiology_agent = PhysiologyAgent()
        comprehensive_report_agent = ComprehensiveReportAgent()

        agents = [
            conditioning_coach_agent,
            motivator_agent,
            nutrition_agent,
            physiology_agent,
            comprehensive_report_agent,
        ]

        tasks = [
            conditioning_coach_agent.create_conditioning_program(),
            motivator_agent.motivate_athlete(),
            nutrition_agent.generate_meal_plan(),
            physiology_agent.generate_physiology_report(),
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


@app.get("/")
def read_root():
    return {"message": "FastAPI CrewAI server is running!"}


@app.options("/update_program")  # ✅ Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}


@app.post("/run_assessment")
async def run_assessment(
    input_text: str = Body(..., media_type="text/plain"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Starts the assessment as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(run_and_store_result, task_id, input_text)
    return {"success": True, "task_id": task_id}

def run_and_store_result(task_id: str, input_text: str):
    """Runs the assessment and stores the result for later retrieval."""
    assessment_crew = AssessmentCrew(input_text)
    result = assessment_crew.run(task_id)  # ✅ Runs synchronously in the background
    task_results[task_id] = result  # ✅ Store result for polling



@app.get("/get_result/{task_id}")
def get_result(task_id: str):
    result = task_results.pop(task_id, "Processing...")
    return {"success": True, "result": result}

