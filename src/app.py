from fastapi import FastAPI
from pydantic import BaseModel
import crewai  # Ensure CrewAI is installed and configured

app = FastAPI()

# Define request body schema
class InputData(BaseModel):
    input: str

# Example CrewAI function
def run_crewai_task(input_text):
    return {"output": f"CrewAI processed: {input_text}"}

@app.post("/run_task")
def run_task(data: InputData):
    return run_crewai_task(data.input)

@app.get("/")
def home():
    return {"message": "CrewAI API is running on Render!"}
