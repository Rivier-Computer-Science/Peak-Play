##################### Training Regiment #########################
from typing import Dict
from .conversable_agent import MyConversableAgent

class TrainingRegimentAgent(MyConversableAgent):
    description = """ 
            I am the TrainingRegimentAgent. 
            My role is to develop and manage training programs for left-handed players. 
            Design workout routines, track progress, and adjust plans based on performance 
            and user feedback.
        """                        
    system_message = """
            You are the TrainingRegimentAgent. 
            Your role is to develop and manage training programs for left-handed players. 
            Design workout routines, track progress, and adjust plans based on performance 
            and user feedback.         
        """
    def __init__(self, **kwargs):
        super().__init__(
                name="TrainingRegimentAgent",
                human_input_mode="NEVER",
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description',self.description),
                **kwargs
            )
        