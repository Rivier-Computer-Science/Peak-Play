###################### Interaction ########################
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .conversable_agent import MyConversableAgent


class InteractionAgent(MyConversableAgent):
    # description = """ 
    #         InteractionAgent is a reliable system proxy designed to facilitate communication and interaction between a human user and the educational system. 
    #         InteractionAgent serves as an intermediary, efficiently relaying requests and responses to ensure smooth and effective academic support. 
    #         """
    
    system_message = """
            You are InteractionAgent, a system proxy for a human user. 
            Your role is to facilitate discussions about athletic training protocols. 
            Understand user queries, identify the relevant topic, and route the 
            query to the appropriate agent. 
            Ensure a friendly and supportive conversation.
            """

    def __init__(self, tutor_agent=None, knowledge_tracer_agent=None, **kwargs):
        super().__init__(
            name="InteractionAgent",
            human_input_mode="ALWAYS",
            system_message=kwargs.pop('system_message', self.system_message),
            description=kwargs.pop('description',self.system_message),
            **kwargs
        )


