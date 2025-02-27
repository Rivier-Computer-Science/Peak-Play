##############
# Run locally:
###############
"""
uvicorn app:app
curl -X GET "http://localhost:8000"
"""

from fastapi import FastAPI, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import uuid
import crewai
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

from src.WebFunctions.run_full_assement import RunFullAssessmentCrew
from src.WebFunctions.analyze_fitbit_data import AnalyzeFitbitDataCrew

import src.Utils.utils as utils

# Import Agents
from src.Agents.agent_helpers import concatente_task_outputs
from src.Agents.base_agent import BaseAgent
from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.comprehensive_report_agent import ComprehensiveReportAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.exercise_database_agent import ExerciseDatabaseAgent
from src.Agents.fitbit_agent import FitbitAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent

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

class AssessmentInput(BaseAgent):
    file_path: str  # WordPress passes file URL or local path

class AssessmentCrew:
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

class UpdateInput(BaseAgent):
    file_path: str  # WordPress passes file URL or local path

class UpdateCrew:
    def __init__(self, player_data: str):
        self.player_data = StringKnowledgeSource(content=player_data)

    def run(self, task_id: str):
        # Initialize agents with file input
       # analyst_agent = AnalystAgent()
        conditioning_coach_agent = ConditioningCoachAgent()
        motivator_agent = MotivatorAgent()
        nutrition_agent = NutritionAgent()
        physiology_agent = PhysiologyAgent()
        comprehensive_report_agent = ComprehensiveReportAgent()

        agents = [
         #   analyst_agent,
            conditioning_coach_agent,
            motivator_agent,
            nutrition_agent,
            physiology_agent,
            comprehensive_report_agent,
        ]

        tasks = [
         #   analyst_agent.analyze_data(),
            conditioning_coach_agent.modify_training_program(),
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
    
class LogCrew:
    def __init__(self, player_data: str):
        self.player_data = StringKnowledgeSource(content=player_data)

    def run(self, task_id: str):
        # Initialize agents with file input
        conditioning_coach_agent = ConditioningCoachAgent()
        motivator_agent = MotivatorAgent()

        agents = [
            conditioning_coach_agent,
            motivator_agent
        ]

        tasks = [
            conditioning_coach_agent.generate_report(),
            motivator_agent.motivate_athlete(),
        ]

        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            knowledge_sources=[self.player_data],
            process=crewai.Process.sequential,
            verbose=True
        )

        result = crew.kickoff()       
        return concatente_task_outputs(result)
    


@app.get("/")
def read_root():
    return {"message": "FastAPI CrewAI server is running!"}

#################################
# Get status of background tasks
#################################
@app.get("/get_result/{task_id}")
def get_result(task_id: str):
    result = task_results.pop(task_id, "Processing...")
    return {"success": True, "result": result}

##################################
# Run Full Assessment
#################################
@app.options("/run_full_assessment")  # Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}

@app.post("/run_full_assessment")
async def run_full_assessment(
    input_text: str = Body(..., media_type="text/plain"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):    
    """Starts the assessment as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(full_assessment_run_and_store_result, task_id, input_text)
    return {"success": True, "task_id": task_id}

def full_assessment_run_and_store_result(task_id: str, input_text: str):
    """Runs the assessment and stores the result for later retrieval."""
    full_assessment_crew = RunFullAssessmentCrew(input_text)
    full_assessment_result = full_assessment_crew.run(task_id)  # Runs synchronously in the background
    task_results[task_id] = full_assessment_result  # Store result for polling


####################
# Analyze Fitbit Data
####################

@app.options("/analyze_fitbit_data")  # Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}

@app.post("/analyze_fitbit_data")
async def analyze_fitbit_data(
    input_text: str = Body(..., media_type="text/plain"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Starts the Update as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(analyze_fitbit_data_run_and_store_result, task_id, input_text)
    return {"success": True, "task_id": task_id}


def analyze_fitbit_data_run_and_store_result(task_id: str, input_text: str):
    """Runs the Update and stores the result for later retrieval."""
    analyze_fitbit_data_crew = AnalyzeFitbitDataCrew(input_text)
    analyze_fitbit_data_result = analyze_fitbit_data_crew.run(task_id)  # Runs synchronously in the background
    task_results[task_id] = analyze_fitbit_data_result  # Store result for polling


####################
# Analyze Log Data
####################

@app.options("/log_training")  # Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}

@app.post("/log_training")
async def analyze_fitbit_data(
    input_text: str = Body(..., media_type="text/plain"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Starts the Update as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(run_and_store_log_result, task_id, input_text)
    return {"success": True, "task_id": task_id}


def run_and_store_log_result(task_id: str, input_text: str):
    """Runs the Update and stores the result for later retrieval."""
    log_crew = LogCrew(input_text)
    log_crew_result = log_crew.run(task_id)  # Runs synchronously in the background
    task_results[task_id] = log_crew_result  # Store result for polling

