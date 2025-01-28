##################### Position Coach Guide #########################
from typing import Dict
from .conversable_agent import MyConversableAgent

class PositionCoach(MyConversableAgent):
    # description = ""
    
    system_message = """
            You are the PositionCoach. 
            Your role is to provide feedback and instruction to players based on their field position.
            Create personalized drills and training plans to refine skills while addressing unique player challenges.
            For all players, provide personalized feedback related to offensive performance (batting).
                       
        """
    def __init__(self, **kwargs):
        super().__init__(
                name="PositionCoach",
                human_input_mode="NEVER",
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description',self.system_message),
                **kwargs
            )
    