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
import json

# Import Crews
from src.Crews.LogCrew import LogCrew
from src.Crews.run_full_assement_crew import RunFullAssessmentCrew
from src.Crews.analyze_fitbit_data_crew import AnalyzeFitbitDataCrew
from src.WebFunctions.generate_blog_post import GenerateBlogPostCrew
from src.Crews.UpdateCrew import UpdateCrew

import src.Utils.utils as utils
import src.Helpers.web_data as web_data

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
    input_text: utils.WordPressInput,
    background_tasks: BackgroundTasks = BackgroundTasks()
):    
    """Starts the assessment as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(full_assessment_run_and_store_result, task_id, input_text.model_dump_json())
    return {"success": True, "task_id": task_id}

def full_assessment_run_and_store_result(task_id: str, input_text):
    """Runs the assessment and stores the result for later retrieval."""
    full_assessment_crew = RunFullAssessmentCrew(input_text)
    full_assessment_result = full_assessment_crew.run(task_id)  # Runs synchronously in the background
    task_results[task_id] = full_assessment_result  # Store result for polling

#########################
# Update Crew
###############

@app.options("/update_program")  # Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}

@app.post("/update_program")
async def run_update_program(
    input_text: web_data.UpdateProgramData,
    background_tasks: BackgroundTasks = BackgroundTasks()
):    
    """Starts the update as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(update_program_and_store_result, task_id, input_text)
    return {"success": True, "task_id": task_id}

def update_program_and_store_result(task_id: str, input_text):
    """Runs the update and stores the result for later retrieval."""
    update_crew = UpdateCrew(player_data=input_text.dict())
    update_crew_result = update_crew.run(task_id)  # Runs synchronously in the background
    task_results[task_id] = update_crew_result  # Store result for polling

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
async def log_training_data(
    input_text: utils.WordPressInput,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Starts the Update as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(run_and_store_log_result, task_id, input_text.model_dump_json())
    return {"success": True, "task_id": task_id}


def run_and_store_log_result(task_id: str, input_text):
    """Runs the Update and stores the result for later retrieval."""
    log_crew = LogCrew(input_text)
    log_crew_result = log_crew.run(task_id)  # Runs synchronously in the background
    task_results[task_id] = log_crew_result  # Store result for polling


#####################
# Generate Blog Post
#####################
@app.options("/generate_blog_post")  # Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight generate_blog_post OK"}

@app.post("/generate_blog_post")
async def generate_blog_post(
    input_text: str = Body(..., media_type="text/plain"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Starts the Update as a background task and returns a task_id."""
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(run_generate_blog_post_and_return_result, task_id, input_text)
    return {"success": True, "task_id": task_id}


def run_generate_blog_post_and_return_result(task_id: str, input_text: str):
    generate_blog_post_crew = GenerateBlogPostCrew()
    generate_blog_post_result, final_blog_post = generate_blog_post_crew.run(task_id)  # Runs synchronously in the background
    print('CrewAI results \n', generate_blog_post_result)
    #task_results[task_id] = final_blog_post  # Store the final blog post
    task_results[task_id] = json.dumps(generate_blog_post_result, indent=2)  # Store the final blog post as a string