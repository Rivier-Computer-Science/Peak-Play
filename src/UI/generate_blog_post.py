from dotenv import load_dotenv
# Load environment variables
load_dotenv("/etc/secrets")

import os
# Disable CrewAI Telemetry (it is a timeout bug)
# Must be called before importing crewai
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true" 

import sys
import logging

import crewai as crewai
import langchain_openai as lang_oai
import crewai_tools as crewai_tools
from src.Helpers.pretty_print_crewai_output import display_crew_output

from src.Crews.blog_writing_crew import BlogWritingCrew
import src.Models.llm_config as llm_config

import src.Utils.utils as utils



# Initialize logger
logger = utils.configure_logger(logging.DEBUG)



if __name__ == "__main__":
    print("## Write Blog Post")
    print('-------------------------------')

    blogging_crew = BlogWritingCrew(logger=logger)
    logger.info("Blog Writing crew initialized successfully")

    try:       
        crew_output, blog_post = blogging_crew.run()
        logger.info("Bloggin crew execution run() successfully")
    except Exception as e:
        logger.error(f"Error during crew execution: {e}")
        sys.exit(1)

    # Display the output
    print("\n\n########################")
    print("## Here is the output")
    print("########################\n")

    display_crew_output(crew_output, llm_config.GPT5MiniConfig())


    print("Collaboration complete")

    print("******* Render Markdown **********")
    from markdown_it import MarkdownIt

    md = MarkdownIt()
    blog_post_md = blog_post["result"]["post_content"]
    html = md.render(blog_post_md)

    print(html)




    sys.exit(0)
