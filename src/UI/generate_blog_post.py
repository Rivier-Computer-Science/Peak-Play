from dotenv import load_dotenv
# Load environment variables
load_dotenv("/etc/secrets")

import sys
import logging

import crewai as crewai
import langchain_openai as lang_oai
import crewai_tools as crewai_tools
from src.Helpers.pretty_print_crewai_output import display_crew_output

from src.Agents.blog_post_agents import BlogTopicAgent, BlogWriterAgent, BlogCriticAgent
from src.Models.llm_config import gpt_4o_llm_random

import src.Utils.utils as utils



# Initialize logger
logger = utils.configure_logger(logging.INFO)

# Randomize LLM for random blog posts


class BlogWritingCrew:

    def run(self):
        blog_topic_agent = BlogTopicAgent(llm=gpt_4o_llm_random)
        blog_writer_agent = BlogWriterAgent(llm=gpt_4o_llm_random)
        blog_critic_agent = BlogCriticAgent(llm=gpt_4o_llm_random)


        agents = [
            blog_topic_agent,
            blog_writer_agent,
            blog_critic_agent
        ]

        tasks = [
            blog_topic_agent.select_blog_topic(),
            blog_writer_agent.write_blog_post(),
            blog_critic_agent.critique_blog_post(),
            blog_writer_agent.revise_blog_post()
        ]
        

        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            process=crewai.Process.sequential,
            verbose=True
        )

        # Register crew with BaseAgent        
        for agent in crew.agents:
            logger.info(f"Agent Name: '{agent.role}'")
            agent.register_crew(crew)

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    print("## Write Blog Post")
    print('-------------------------------')

    blogging_crew = BlogWritingCrew()
    logger.info("Blog Writing crew initialized successfully")

    try:       
        crew_output = blogging_crew.run()
        logger.info("Bloggin crew execution run() successfully")
    except Exception as e:
        logger.error(f"Error during crew execution: {e}")
        sys.exit(1)

    # Display the output
    print("\n\n########################")
    print("## Here is the output")
    print("########################\n")

    display_crew_output(crew_output)

    print("Collaboration complete")
    sys.exit(0)
