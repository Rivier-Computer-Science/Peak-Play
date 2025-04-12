import crewai as crewai

from src.Crews.blog_writing_crew import BlogWritingCrew
import src.Agents.agent_helpers as agent_helpers
import src.Utils.utils as utils



class GenerateBlogPostCrew:
    def run(self, task_id: str):
        blog_writing_crew = BlogWritingCrew()

        result, _ = blog_writing_crew.run()

        return agent_helpers.concatente_task_outputs(result)