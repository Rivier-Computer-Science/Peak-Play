#######################################################################
# Agents
# - BlogTopicAgent: Select sport and topic
# - BlogWriterAgent: Write the blog post and improve it based on critique
# - BlogCriticAgent: Critique the blog post
########################################################################

import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class BlogTopicAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Blog Topic Selector Agent for topics related to athletes.
            """
    
        goal = """
            Pick a random sport from the entirety of possible sports. After picking a sport, pick a 
                 topic for that sport. Topics may include how to improve performance but they may also
                 include advice such as nutrition, conditioning training, beneficial exercises, strategy
                 about the selected sport, psychology, or motiviation. You can also select your own topic.
                 Pick only 1 topic. Do not suggest multiple topics or combine topics.
            """

        backstory = """
            You are an expert athlete analyst who has been selecting blog topics for decades. You know many
            different sports and can select topics that are interesting to athletes of all levels but you 
            particularly focus on new and intermediate level athletes - both male and female - and those
            with physical challenges (e.g., parathletes) and special capabilities (e.g., left handed).
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def select_blog_topic(self, age: str = '21'): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Pick a sport. Then pick a topic within the sport. Occasionally, but not always,
                    select a topic for physically challenged athletes (e.g., parathletes) or those with special
                    capabilities (e.g., left handed).
            """),
            agent=self,
            expected_output="A sport and blog topic for that sport."
        )  



class BlogWriterAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Blog Writer Agent.
            """
    
        goal = """
            Given a sport and a topic, write a blog post.
            """

        backstory = """
            You are an expert blog writer. You've been blogging for 20+ years about different sports
                and topics to improve athlete performance. You primarily write for amateur Athletes.

            You construct blog posts that are concise, witty, and memorable.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def write_blog_post(self, age: str = '21'): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Write a blog post about the chosen sport and topic.
                            
                It should be consice, witty, and memorable.
            """),
            agent=self,
            expected_output="A blog post written using markdown"
        )        

    def revise_blog_post(self, age: str = '21'): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Revise and improve the blog post based on critiques of the working version.
            """),
            agent=self,
            expected_output="An improved blog post written using markdown"
        )  


class BlogCriticAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Blog Critic Agent.
            """
    
        goal = """
            Critique the blog post written by the Blog Writer Agent.
            """

        backstory = """
            You are an expert blog writing critic. You have been reading athlete blogs for decades.
            You are also an expert in grammar and style. You know how to provide feedback to improve
                audience response to blog posts.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def critique_blog_post(self, age: str = '21'): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Critique the blog post and suggest improvements.

            """),
            agent=self,
            expected_output="Actionable advice to improve the blog post."
        )      