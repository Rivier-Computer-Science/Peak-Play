##################### Nutrition Guide #########################
from typing import Dict
from .conversable_agent import MyConversableAgent

class NutritionGuideAgent(MyConversableAgent):
    # description = ""
    
    system_message = """
            You are the NutritionGuideAgent. 
            Your role is to offer nutrition advice tailored to athletes. 
            Create personalized meal plans, provide dietary tips, and monitor nutritional intake 
            based on user input.            
        """
    def __init__(self, **kwargs):
        super().__init__(
                name="NutritionGuideAgent",
                human_input_mode="NEVER",
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description',self.system_message),
                **kwargs
            )
    