from dotenv import load_dotenv
import os
load_dotenv()
for key, value in os.environ.items():
    print(f"{key}: {value}")

import sys
import logging
import crewai as crewai
import langchain_openai as lang_oai
import crewai_tools as crewai_tools
from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from src.Helpers.pretty_print_crewai_output import display_crew_output


from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent

# Initialize logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)



class AssessmentCrew:
  def __init__(self):
      self.is_init = True

  def run(self):

    player_profile = TextFileKnowledgeSource(
       file_paths=["player_profile.txt"]
    )

    # assignment_to_course_outcomes_source = ExcelKnowledgeSource(
    #    file_paths=["comp_405_assignment_to_course_outcomes_map.xlsx"]
    # )
    # course_outcomes_agent = CourseOutcomesAgent(knowledge_sources=[grades_source, assignment_to_course_outcomes_source])

    biomechanics_coach_agent = BiomechanicsCoachAgent()
    conditioning_coach_agent = ConditioningCoachAgent()
    motivator_agent = MotivatorAgent()
    nutrition_agent = NutritionAgent()
    physiology_agent = PhysiologyAgent()
    position_coach_agent = PositionCoachAgent()
    psychology_agent = PsychologyAgent()


    agents = [ biomechanics_coach_agent, 
               conditioning_coach_agent,
               motivator_agent,
               nutrition_agent,
               physiology_agent,
               position_coach_agent,
               psychology_agent,
             ]

    tasks = [ biomechanics_coach_agent.analyze_biometrics(),
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
        verbose=True
    )

    for agent in crew.agents:
      logger.info(f"Agent Name: '{agent.role}'")

    result = crew.kickoff()

    return result

if __name__ == "__main__":
    print("## Assessment Analysis")
    print('-------------------------------')
  
    assessment_crew = AssessmentCrew()
    logging.info("Assessment crew initialized successfully")

    try:
        crew_output = assessment_crew.run()
        logging.info("Assessment crew execution run() successfully")
    except Exception as e:
        logging.error(f"Error during crew execution: {e}")
        sys.exit(1)
    
    # Accessing the crew output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboration complete")
    sys.exit(0)
