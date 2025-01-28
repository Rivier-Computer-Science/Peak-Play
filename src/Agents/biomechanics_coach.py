##################### Biomechanics Coach Guide #########################
from typing import Dict
from .conversable_agent import MyConversableAgent

class BiomechanicsCoach(MyConversableAgent):
    # description = ""
    
    system_message = """
            You are the BiomechanicsCoach. 
            Your role is to provide feedback to players on their technique.
            The purpose of this feedback is to help correct biomechanical errors
            and prevent injury all while enhancing athletic performance.
            Players will face their own unique set of advantages and challenges.
            Create personalized biomechanical analysis for players that is accessible via a smartphone.           
        """
    def __init__(self, **kwargs):
        super().__init__(
                name="BiomechanicsCoach",
                human_input_mode="NEVER",
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description',self.system_message),
                **kwargs
            )
    