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

import src.Utils.utils as utils



# Initialize logger
logger = utils.configure_logger(logging.INFO)



class MotivationCrew:
    def __init__(self, input_file_path="data/pitcher_10yrs_old_profile.txt"):        
        self.knowledge_data = utils.get_knowledge_type(input_file_path)

    def run(self):
        # Initialize agents with the player profile
        biomechanics_coach_agent = BiomechanicsCoachAgent()
        conditioning_coach_agent = ConditioningCoachAgent()
        exercise_database_agent = ExerciseDatabaseAgent()
        fitbit_agent = FitbitAgent()
        motivator_agent = MotivatorAgent()
        nutrition_agent = NutritionAgent()
        physiology_agent = PhysiologyAgent()
        position_coach_agent = PositionCoachAgent()
        psychology_agent = PsychologyAgent()
        comprehensive_report_agent = ComprehensiveReportAgent()

        agents = [
            motivator_agent, psychology_agent, 
        ]

        tasks = [
            motivator_agent.motivate_athlete(),
        ]
        

        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            #knowledge_sources=[self.knowledge_data],
            process=crewai.Process.sequential,
            verbose=True
        )

        # Register crew with BaseAgent        
        for agent in crew.agents:
            logger.info(f"Agent Name: '{agent.role}'")
            agent.register_crew(crew)

        result = crew.kickoff()
        return result


def run_motivation_update(player_profile_file: str = "data/pitcher_10yrs_old_profile.txt"):
    motivation_crew = MotivationCrew(input_file_path=player_profile_file)
    logger.info(f"Motivation crew initialized successfully for {player_profile_file}")

    try:
        crew_output = motivation_crew.run()
        logger.info(f"Motivation crew execution run() successfully for file {player_profile_file}")
    except Exception as e:
        logger.error(f"Error during crew execution of {player_profile_file}: {e}")
        sys.exit(1)

    # Display the output
    print("\n\n##########################################################")
    print(f"## Here is the Report for {player_profile_file}")
    print("############################################################\n")

    display_crew_output(crew_output)


if __name__ == "__main__":
    print("## Motivation Update")
    print('-------------------------------')

    run_motivation_update("data/pitcher_10yrs_old_profile.txt")
    run_motivation_update("data/pitcher_16yrs_old_profile.txt")

    print("Collaboration complete")
    sys.exit(0)