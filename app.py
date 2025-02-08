from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import crewai as crewai
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent

# Initialize FastAPI app
app = FastAPI()

# Enable CORS with explicit OPTIONS method
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
    input: str

class AssessmentCrew:
    def __init__(self):
        self.is_init = True

    def run(self, input_text: str, task_id: str):
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
            biomechanics_coach_agent.analyze_biometrics(input_text),
            conditioning_coach_agent.create_conditioning_program(input_text),
            motivator_agent.motivate_athelete(input_text),
            nutrition_agent.generate_meal_plan(input_text),
            physiology_agent.generate_physiology_report(input_text),
            position_coach_agent.generate_position_advice(input_text),
            psychology_agent.generate_psychology_report(input_text)
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
        
        # Store result in memory
        task_results[task_id] = result

@app.options("/run_assessment")  # ✅ Allow OPTIONS requests for CORS
def preflight_check():
    return {"message": "Preflight OK"}

@app.post("/run_assessment")
def run_assessment(input_data: AssessmentInput, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    background_tasks.add_task(AssessmentCrew().run, input_data.input, task_id)
    
    return {"success": True, "task_id": task_id}

@app.get("/get_result/{task_id}")
def get_result(task_id: str):
    result = task_results.get(task_id, "Processing...")
    return {"success": True, "result": result}
