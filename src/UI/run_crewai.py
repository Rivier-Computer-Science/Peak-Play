from dotenv import load_dotenv
import os
import sys
import logging
import json
import pathlib as Path

import crewai as crewai
import langchain_openai as lang_oai
import crewai_tools as crewai_tools
from src.Helpers.pretty_print_crewai_output import display_crew_output
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource


from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent
from src.Agents.comprehensive_report_agent import ComprehensiveReportAgent

# Load environment variables
load_dotenv("/etc/secrets")

# Initialize logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)




class AssessmentCrew:
    def __init__(self, input_file_path="data/player_profile.txt"):        
        self.input_file_path = input_file_path
        self.knowledge_data = self.get_knowledge_type()

    def get_knowledge_type(self):        
        if not self.input_file_path:
            return "Error: No input file provided."
        
        # Handle JSON input
        if self.input_file_path.endswith(".json"):
            return JSONKnowledgeSource(file_paths=[self.input_file_path])

        # Handle TXT input
        elif self.input_file_path.endswith(".txt"):
            try:
                with open(self.input_file_path, "r", encoding="utf-8") as file:
                    return StringKnowledgeSource(content=file.read())
            except FileNotFoundError:
                return f"Error: File '{self.input_file_path}' not found."
            except Exception as e:
                return f"Error reading file: {e}"
                       
        # Unsupported file type
        else:
            return "Error: Unsupported file format. Please provide a .txt or .json file."



    def run(self):
        # Initialize agents with the player profile
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
            knowledge_sources=[self.knowledge_data],
            process=crewai.Process.sequential,
            verbose=True
        )

        # Register crew with BaseAgent        
        for agent in crew.agents:
            logger.info(f"Agent Name: '{agent.role}'")
            agent.register_crew(crew)

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    print("## Assessment Analysis")
    print('-------------------------------')

    assessment_crew = AssessmentCrew()
    logging.info("Assessment crew initialized successfully")

    try:
        crew_output = assessment_crew.run()
        #crew_output = assessment_crew.run(inputs={"job": "Create a comprehensive overview of the athlete"})
        logging.info("Assessment crew execution run() successfully")
    except Exception as e:
        logging.error(f"Error during crew execution: {e}")
        sys.exit(1)

    # Display the output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboration complete")
    sys.exit(0)
