from dotenv import load_dotenv
# Load environment variables
load_dotenv("/etc/secrets")

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
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource


from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent
from src.Agents.comprehensive_report_agent import ComprehensiveReportAgent
from src.Agents.exercise_database_agent import ExerciseDatabaseAgent
from src.Agents.fitbit_agent import FitbitAgent
from src.Helpers.athlete_example_profiles import jane_smith_tennis, john_doe_soccer

import src.Utils.utils as utils



# Initialize logger
logger = utils.configure_logger(logging.INFO)



class AssessmentCrew:

    def run(self):
        # Initialize agents with the player profile
        # biomechanics_coach_agent = BiomechanicsCoachAgent()
        # conditioning_coach_agent = ConditioningCoachAgent()
        # exercise_database_agent = ExerciseDatabaseAgent()
        # fitbit_agent = FitbitAgent()
        # motivator_agent = MotivatorAgent()
        # nutrition_agent = NutritionAgent()
        # physiology_agent = PhysiologyAgent()
        position_coach_agent = PositionCoachAgent(athlete_profile=jane_smith_tennis)
        # psychology_agent = PsychologyAgent()
        # comprehensive_report_agent = ComprehensiveReportAgent()

        agents = [
            position_coach_agent,
        ]

        tasks = [
            position_coach_agent.generate_position_advice(),
        ]
        

        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
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
    logger.info("Assessment crew initialized successfully")

    try:
        crew_output = assessment_crew.run()
        #crew_output = assessment_crew.run(inputs={"job": "Create a comprehensive overview of the athlete"})
        logger.info("Assessment crew execution run() successfully")
    except Exception as e:
        logger.error(f"Error during crew execution: {e}")
        sys.exit(1)

    # Display the output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboration complete")
    sys.exit(0)