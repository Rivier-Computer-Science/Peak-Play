from dotenv import load_dotenv
import os
import sys
import logging
import crewai as crewai
import langchain_openai as lang_oai
import crewai_tools as crewai_tools
from src.Helpers.pretty_print_crewai_output import display_crew_output

from src.Agents.biomechanics_coach_agent import BiomechanicsCoachAgent
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.nutrition_agent import NutritionAgent
from src.Agents.physiology_agent import PhysiologyAgent
from src.Agents.position_coach_agent import PositionCoachAgent
from src.Agents.psychology_agent import PsychologyAgent

# Load environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


class AssessmentCrew:
    def __init__(self, input_file="knowledge/player_profile.txt"):
        self.input_file = input_file

    def _read_player_profile(self):
        """Reads the player profile file and returns its contents."""
        try:
            with open(self.input_file, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Error: {self.input_file} not found.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading file {self.input_file}: {e}")
            sys.exit(1)

    def run(self):
        """Runs the assessment using the player profile data."""
        player_data = self._read_player_profile()

        # Initialize agents with the player profile
        biomechanics_coach_agent = BiomechanicsCoachAgent(input_file=self.input_file)
        conditioning_coach_agent = ConditioningCoachAgent(input_file=self.input_file)
        motivator_agent = MotivatorAgent(input_file=self.input_file)
        nutrition_agent = NutritionAgent(input_file=self.input_file)
        physiology_agent = PhysiologyAgent(input_file=self.input_file)
        position_coach_agent = PositionCoachAgent(input_file=self.input_file)
        psychology_agent = PsychologyAgent(input_file=self.input_file)

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
            biomechanics_coach_agent.analyze_biometrics(),
            conditioning_coach_agent.create_conditioning_program(),
            motivator_agent.motivate_athlete(),
            nutrition_agent.generate_meal_plan(),
            physiology_agent.generate_physiology_report(),
            position_coach_agent.generate_position_advice(),
            psychology_agent.generate_psychology_report(),
        ]

        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
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

    # Display the output
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboration complete")
    sys.exit(0)
