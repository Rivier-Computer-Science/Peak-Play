##################### Training Regiment #########################
from typing import Dict
from .conversable_agent import MyConversableAgent

class TrainingReportAgent(MyConversableAgent):
    description = """ 
            I am the TrainingReportAgent. 
            My role is to provide constructive feedback based on user training input. 
            Nicely critique their form and provide some tips for inprovment.
        """                        
    system_message = """
            You are the TrainingReportAgent. 
            Your role is to provide constructive feedback based on user training input. 
            Nicely critique their form and provide some tips for inprovment.       
        """
    def __init__(self, **kwargs):
        super().__init__(
                name="TrainingReportAgent",
                human_input_mode="NEVER",
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description',self.description),
                **kwargs
            )
        