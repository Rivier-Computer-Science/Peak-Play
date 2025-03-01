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
    def __init__(self, athlete_profile_file_path: str =None, athlete_age: str = '21'):      
        if(athlete_profile_file_path == None):
            logger.error("player_profile_file_path must be specified")
        
        self.player_profile_file_path = athlete_profile_file_path
        self.knowledge_data = utils.get_knowledge_type(athlete_profile_file_path)
        self.athlete_age = athlete_age

    def run(self):
        motivator_agent = MotivatorAgent(athlete_age=self.athlete_age)
        psychology_agent = PsychologyAgent(athlete_age=self.athlete_age)

        agents = [
             psychology_agent, motivator_agent,
        ]

        tasks = [
            motivator_agent.motivate_athlete(),
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
        display_crew_output(result)

        return result



if __name__ == "__main__":
    print("## Motivation Update")
    print('-------------------------------')

    print("\n\n##########################################################")
    print(f"## Starting 10 year old profile")
    print("############################################################\n")
    pitcher_10yr_old_file_path = "data/pitcher_10yrs_old_profile.txt"
    pitcher_10yr_crew = MotivationCrew(athlete_profile_file_path= pitcher_10yr_old_file_path, 
                                       athlete_age='10')
    logger.info(f"Motivation crew initialized successfully for {pitcher_10yr_old_file_path}")
    pitcher_10yr_crew.run()

    print("\n\n##########################################################")
    print(f"## Starting 16 year old profile")
    print("############################################################\n")
    pitcher_16yr_old_file_path = "data/pitcher_16yrs_old_profile.txt"
    pitcher_16yr_crew = MotivationCrew(athlete_profile_file_path=pitcher_16yr_old_file_path, 
                                       athlete_age='16')
    logger.info(f"Motivation crew initialized successfully for {pitcher_16yr_old_file_path}")
    pitcher_16yr_crew.run()

    print("All Tasks are complete")
    sys.exit(0)