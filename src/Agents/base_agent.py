from openai import OpenAI
import os
import json
import pandas as pd
import src.Models.llm_config as llm_config
import crewai as crewai
from pydantic import BaseModel, ConfigDict
import logging


class BaseAgent(crewai.Agent):
    model_config = ConfigDict(extra='allow',arbitrary_types_allowed=True)

    def __init__(self, **kwargs):                                        
        super().__init__(
            #name=kwargs.pop('name', 'Helpful Agent'),
            #role=role,
            #goal=goal,
            #backstory=backstory,
            #tools=kwargs.get('tools', []),   #[my_tool1, my_tool2],  # Optional, defaults to an empty list
            llm=kwargs.pop('llm', llm_config.gpt_4o_llm),
            allow_delegation=kwargs.pop('allow_delegation', False),
            #function_calling_llm=my_llm,  # Optional
            max_iter=kwargs.pop('max_iter', 15),  # Optional
            max_rpm=kwargs.pop('max_rpm', 60*4), # Optional
            max_execution_time=kwargs.pop('max_execution_time', None), # Optional
            verbose=kwargs.pop('verbose', True),  # Optional
            #step_callback=my_intermediate_step_callback,  # Optional
            cache=kwargs.pop('cache', True),  # Optional
            #system_template=my_system_template,  # Optional
            #prompt_template=my_prompt_template,  # Optional
            #response_template=my_response_template,  # Optional
            #config=my_config,  # Optional
            #crew=my_crew,  # Optional
            #tools_handler=my_tools_handler,  # Optional
            #cache_handler=my_cache_handler,  # Optional
            #callbacks=[callback1, callback2],  # Optional
            allow_code_execution=kwargs.pop('allow_code_execution', False),  # Optiona
            max_retry_limit=kwargs.pop('max_retry_limit', 2),  # Optional
            **kwargs
        )        

        # Initialize the logger
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            # Set up logging format and level if not already configured
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)



    def register_crew(self, crew):
        self.crew = crew


 

