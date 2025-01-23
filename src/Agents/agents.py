import autogen
import os
from .interaction_agent import InteractionAgent
from .nutrition_guide_agent import NutritionGuideAgent
from .training_regiment_agent import TrainingRegimentAgent
from .training_report_agent import TrainingReportAgent

from src.Models.llm_config import gpt4_config
from enum import Enum

os.environ["AUTOGEN_USE_DOCKER"] = "False"

###############################################
# ChatGPT Model
###############################################
llm = gpt4_config

#################################################
# Define Agents
#################################################

interaction_agent = InteractionAgent(llm_config=llm)
nutrition_guide_agent = NutritionGuideAgent(llm_config=llm)
training_regiment_agent = TrainingRegimentAgent(llm_config=llm)
training_report_agent = TrainingReportAgent(llm_config=llm)


class AgentKeys(Enum):    
    INTERACTION_AGENT = 'interaction_agent'
    NUTRITION_GUIDE_AGENT = 'nutrition_guide_agent'
    TRAINING_REGIMENT_AGENT = 'training_regiment_agent'
    TRAINING_REPORT_AGENT = 'training_report_agent'


agents_dict = {
    AgentKeys.INTERACTION_AGENT.value: interaction_agent,
    AgentKeys.NUTRITION_GUIDE_AGENT.value: nutrition_guide_agent,
    AgentKeys.TRAINING_REGIMENT_AGENT.value: training_regiment_agent,
    AgentKeys.TRAINING_REPORT_AGENT.value: training_report_agent
 }

agents_dict_by_name = {
    "InteractionAgent": interaction_agent,
    "NutritionGuideAgent": nutrition_guide_agent,
    "TrainingRegimentAgent": training_regiment_agent, 
    "TrainingReportAgent": training_report_agent   
}

avatars = {
    interaction_agent.name: "✏️",                 # Pencil
    nutrition_guide_agent.name: "🧑‍🎓",            # Person with graduation hat
    training_regiment_agent.name:"💪", 
    training_report_agent.name: "🏋️‍♂️"
}
