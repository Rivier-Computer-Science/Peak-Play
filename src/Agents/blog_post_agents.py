#######################################################################
# Agents
# - BlogTopicAgent: Select sport and topic
# - BlogWriterAgent: Write the blog post and improve it based on critique
# - BlogCriticAgent: Critique the blog post
########################################################################

import crewai as crewai
from textwrap import dedent

from pydantic import BaseModel

from src.Agents.base_agent import BaseAgent
from src.AgentTools.search_wikipedia import search_wikipedia
from src.AgentTools.search_unsplash_images import search_unsplash_images


class BlogPostResult(BaseModel):
    post_title: str
    post_content: str
    post_tags: str

class BlogPostOutput(BaseModel):
    success: str
    result: BlogPostResult

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
                Check your long term memory.
                Then pick a sport using a uniform distribution so you don't always pick the same sport. 
                    Then pick a topic within the sport. If the sport has been covered before, don't repeat the topic.
                Occasionally, but not always, select a topic for physically challenged athletes (e.g., parathletes) or those with special
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

            If you use unsplash, be sure to credit the website and photographer. Do not make up the
                               the attribution. It always comes back in the response.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[search_wikipedia, search_unsplash_images],
            **kwargs
        )

    def write_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Write a blog post about the chosen sport and topic.
                            
                It should be consice, witty, and memorable.
                               
                If you use unsplash, be sure to credit the website and photographer. Do not make up the
                               the attribution. It always comes back in the response.
            """),
            agent=self,
            output_json=BlogPostOutput,
            expected_output="A JSON blog post with markdown as a string"
        )        

    def revise_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Revise and improve the blog post based on critiques of the working version.
                               
                If you use unsplash, be sure to credit the website and photographer. Do not make up the
                               the attribution. It always comes back in the response.
            """),
            agent=self,
            output_json=BlogPostOutput,
            expected_output="An improved JSON blog post with markdown as a string"
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

    def critique_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Critique the blog post and suggest improvements.

            """),
            agent=self,
            expected_output="Actionable advice to improve the blog post."
        )      
    

class BlogValidationAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Blog Validation Agent. You make sure that all content in the blog post exists and is accurate"
            """
    
        goal = """
            Check all information in the blog post written by the Blog Writer Agent for correctness and existance.
            """

        backstory = """
            You are an expert in finding hallucinated data and incorrect information in blog posts.
            You also check all external references in the blog post and identify incorrect links.
                        
            You have been reading athlete blogs for decades and can easily spot incorrect information in blog posts.
            You provide corrected information and revise the blog post if needed.
            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[search_wikipedia, search_unsplash_images],
            **kwargs
        )

    def validate_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(f"""
                Look for incorrect links and/or incorrect data.
                Find hallucinated information and revise it.
                               
                If example.com has been used, replace it with an equivalent real link or delete it.
                               
                Update the blog post with only correct information.
                               
                If you use unsplash, be sure to credit the website and photographer. Do not make up the
                               the attribution. It always comes back in the response.

            """),
            agent=self,
            expected_output="A revised blog post with corrected links and information."
        )       
    

class BlogPublisherAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            You are the Blog Post Publisher Agent. 
            You make a final check of the blog post and revise it if needed for publications.        
            """
    
        goal = """
            Check all information in the blog post and revise it if needed so that it can be published.
            """

        backstory = """
            You are an expert in the publishing of blog posts.

            You have been the final editor and publisher of blog posts for decades.

            You have great grammar and spelling capabilities in addition to coordinating edits form multiple agents.

            You aggregate all input and changes and make the final decision on what gets published.

            You NEVER publish content that says "insert here". You either find the appropriate reference or delete
                the "insert here" text.

            """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )


    def publish_blog_post(self): 
        return crewai.Task(
            description=dedent("""
                You consider all the information the agents have provided.
                You make final edits based on your years of experience.
                You revise the blog post for publication.
                Add appropriate WordPress tags in the post_tags field as plain text. No markdown.

                The output must strictly follow this exact JSON format:

                {
                    "success": true,
                    "result": {
                        "post_title": "A short and descriptive blog title",
                        "post_content": "Detailed markdown content **WITHOUT** the title..."
                        "post_tags": "Wordpress tags"
                    }
                }

                Important rules:
                - Do NOT wrap your JSON in markdown code blocks or backticks.
                - Do NOT include any explanatory text or additional formatting.
                - ONLY output valid JSON exactly as shown above.

                Ensure the markdown content is detailed, engaging, and properly formatted.
            """),
            agent=self,
            output_json=BlogPostOutput,
            expected_output=dedent("""
                {
                    "success": true,
                    "result": {
                        "post_title": "A short and descriptive blog title",
                        "post_content": "Detailed markdown content **WITHOUT** the title..."
                        "post_tags": "Wordpress tags"
                    }
                }
            """)
        )
      