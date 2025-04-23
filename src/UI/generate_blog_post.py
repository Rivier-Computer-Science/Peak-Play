from dotenv import load_dotenv
# Load environment variables
load_dotenv("/etc/secrets")

import sys
import logging

import crewai as crewai
import langchain_openai as lang_oai
import crewai_tools as crewai_tools
from src.Helpers.pretty_print_crewai_output import display_crew_output

from src.Crews.blog_writing_crew import BlogWritingCrew
from src.Models.llm_config import gpt_4o_llm_blog_post

import src.Utils.utils as utils



# Initialize logger
logger = utils.configure_logger(logging.INFO)

# Randomize LLM for random blog posts




if __name__ == "__main__":
    print("## Write Blog Post")
    print('-------------------------------')

    blogging_crew = BlogWritingCrew()
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

    display_crew_output(crew_output)


    print("Collaboration complete")
    sys.exit(0)
