##############
# Run locally:
###############
"""
uvicorn app:app --reload
curl -X POST "https://localhost:8000" \
     -H "Content-Type: application/json" \
     -d '{"input": "Analyze this athlete\'s performance"}'
"""
#
#############
# run remote:
#############
"""
curl -X POST "https://peakplay.onrender.com/run_assessment" \
     -H "Content-Type: application/json" \
     -d '{"input": "Analyze this athlete\'s performance"}'
"""

from fastapi import FastAPI, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import uuid

from src.WebFunctions.run_full_assement import RunFullAssessmentCrew
from src.WebFunctions.analyze_user_data import AnalyzeUserDataCrew

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

#################################
# Check if backend available
################################
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
# Analyze User Data
####################

@app.options("/analyze_user_data")  # Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}

@app.post("/analyze_user_data")
async def analyze_user_data(
    input_text: str = Body(..., media_type="text/plain"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Starts the Update as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(analyze_user_data_run_and_store_result, task_id, input_text)
    return {"success": True, "task_id": task_id}


def analyze_user_data_run_and_store_result(task_id: str, input_text: str):
    """Runs the Update and stores the result for later retrieval."""
    analyze_user_data_crew = AnalyzeUserDataCrew(input_text)
    analyze_user_data_result = analyze_user_data_crew.run(task_id)  # Runs synchronously in the background
    task_results[task_id] = analyze_user_data_result  # Store result for polling




