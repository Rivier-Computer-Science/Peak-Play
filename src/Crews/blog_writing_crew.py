#######################################################################
# Agents
# - BlogTopicAgent: Select sport and topic
# - BlogWriterAgent: Write the blog post and improve it based on critique
# - BlogCriticAgent: Critique the blog post
# - BlogValidationAgent: Fact-check and fix
# - BlogPublisherAgent: Final packaging
#######################################################################

import os

import crewai as crewai
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.memory import LongTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

import logging
import pprint

# Agents
from src.Agents.BlogAgents.blog_topic_agent import BlogTopicAgent
from src.Agents.BlogAgents.blog_writer_agent import BlogWriterAgent
from src.Agents.BlogAgents.blog_critic_agent import BlogCriticAgent
from src.Agents.BlogAgents.blog_validation_agent import BlogValidationAgent
from src.Agents.BlogAgents.blog_publisher_agent import BlogPublisherAgent

import src.Models.llm_config as llm_config
import src.Agents.agent_helpers as agent_helpers
import src.Utils.utils as utils


class BlogWritingCrew:
    def __init__(self,  llm: crewai.LLM, logger: logging.Logger = None):        
        self.llm = llm
        if logger is None:
            self.logger = utils.configure_logger()
        else:
            self.logger = logger

        self.logger.debug("INIT BLOG WRITING CREW\n%s", pprint.pprint(llm, width=80))


    def run(self):
        blog_topic_agent  = BlogTopicAgent(llm=self.llm)
        blog_writer_agent = BlogWriterAgent(llm=self.llm)
        blog_critic_agent = BlogCriticAgent(llm=self.llm)
        blog_validation_agent = BlogValidationAgent(llm=self.llm)
        blog_publisher_agent = BlogPublisherAgent(llm=self.llm)
        
        agents = [
            blog_topic_agent,
            blog_writer_agent,
            blog_critic_agent,
            blog_validation_agent,
            blog_publisher_agent
        ]

        publish_blog_post = blog_publisher_agent.publish_blog_post()
        tasks = [
            blog_topic_agent.select_blog_topic(),
            blog_writer_agent.write_blog_post(),
            blog_critic_agent.critique_blog_post(),
            blog_writer_agent.revise_blog_post(),
            #blog_critic_agent.critique_blog_post(),
            #blog_writer_agent.revise_blog_post(),
            blog_validation_agent.validate_blog_post(),
            publish_blog_post
        ]
        
       
        long_term_memory=LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path="./blog_post_long_term_memory.db"
            )
        )

        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            memory=True,
            long_term_memory=long_term_memory,
            process=crewai.Process.sequential,
            verbose=True
        )

        # Register crew with BaseAgent        
        for agent in crew.agents:
            self.logger.info(f"Agent Name: '{agent.role}'")
            agent.register_crew(crew)

        result = crew.kickoff()
        blog_post = publish_blog_post.output
        return    result, blog_post.json_dict
