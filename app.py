from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import crewai as crewai
from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent
from src.Agents.comprehensive_report_agent import ComprehensiveReportAgent

# Initialize FastAPI app
app = FastAPI()

# Enable CORS to allow requests from WordPress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with your WordPress domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # ✅ Explicitly allow OPTIONS
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FastAPI CrewAI server is running!"}

# Store task results
task_results = {}

class AssessmentInput(BaseModel):
    file_path: str  # WordPress passes file URL or local path

class AssessmentCrew:
    def __init__(self, input_file: str):
        self.input_file = input_file

    def run(self, task_id: str):
        # Initialize agents with file input
        biomechanics_coach_agent = BiomechanicsCoachAgent(input_file=self.input_file)
        conditioning_coach_agent = ConditioningCoachAgent(input_file=self.input_file)
        motivator_agent = MotivatorAgent(input_file=self.input_file)
        nutrition_agent = NutritionAgent(input_file=self.input_file)
        physiology_agent = PhysiologyAgent(input_file=self.input_file)
        position_coach_agent = PositionCoachAgent(input_file=self.input_file)
        psychology_agent = PsychologyAgent(input_file=self.input_file)
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
            process=crewai.Process.sequential,
            verbose=False
        )

        result = crew.kickoff()
        
        # Store result in memory
        task_results[task_id] = result

@app.options("/run_assessment")  # ✅ Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}

@app.post("/run_assessment")
def run_assessment(input_data: AssessmentInput, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(AssessmentCrew(input_data.file_path).run, task_id)
    
    return {"success": True, "task_id": task_id}

@app.get("/get_result/{task_id}")
def get_result(task_id: str):
    result = task_results.get(task_id, "Processing...")
    return {"success": True, "result": result}
