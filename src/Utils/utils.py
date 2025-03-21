import logging
import json
from typing import Dict, Any

from pydantic import BaseModel # JSON input from WordPress

from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource

class WordPressInput(BaseModel):
    form_data: Dict[str, Any]


def convert_player_profile(player_profile) -> str:
    if player_profile is not None:
        
        if isinstance(player_profile, str):
            return player_profile
        elif isinstance(player_profile, dict):
            return json.loads(player_profile)
        else:
            raise ValueError("player_profile must be a dict or a valid JSON string.")
        
    else: # default profile
        return '''{
                "athlete_name": "John Doe",
                "athlete_age": 25,
                "sex": "male",
                "primary_sport": "soccer",
                "primary_sport_level": "recreational player",
                "secondary_sport": "basketball",
                "secondary_sport_level": "recreational player",
                "unique_aspect": "exceptional agility"
        }'''



def get_knowledge_type(input_file_path:str):        
    if not input_file_path:
        return "Error: No input file provided."
    
    # Handle JSON input
    if input_file_path.endswith(".json"):
        return JSONKnowledgeSource(file_paths=[input_file_path])

    # Handle TXT input
    elif input_file_path.endswith(".txt"):
        try:
            with open(input_file_path, "r", encoding="utf-8") as file:
                return StringKnowledgeSource(content=file.read())
        except FileNotFoundError:
            return f"Error: File '{input_file_path}' not found."
        except Exception as e:
            return f"Error reading file: {e}"
                    
    # Unsupported file type
    else:
        return "Error: Unsupported file format. Please provide a .txt or .json file."

import logging

def configure_logger(
    logLevel: int = logging.DEBUG, 
    logger: logging.Logger = None
) -> logging.Logger:
    """Configures and returns a logger with the specified log level."""
    
    if logger is None:
        logger = logging.getLogger(__name__)  

    logger.setLevel(logLevel)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(module)s - %(filename)s - %(funcName)s - line %(lineno)d - %(asctime)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
