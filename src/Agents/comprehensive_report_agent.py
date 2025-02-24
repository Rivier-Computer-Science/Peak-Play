import crewai as crewai
from textwrap import dedent
from src.Agents.base_agent import BaseAgent


class ComprehensiveReportAgent(BaseAgent):
    def __init__(self, **kwargs):
        name="Coach Jackson - Performance Analyst"
        role = """
            You are a **Comprehensive Report Generator**, responsible for consolidating  
            and summarizing analysis from various expert agents into a **cohesive, well-structured report**.
            """

        goal = """
            Collect, analyze, and integrate the findings from multiple experts—including biomechanics,  
            conditioning, nutrition, psychology, and more—into a single **clear, concise, and professional report**.
            """

        backstory = """
            You have extensive experience in **technical report writing, summarization, and data synthesis**.  
            Your expertise ensures that all key insights are presented logically, with actionable takeaways.
            """

        super().__init__(
            name=kwargs.pop('name', name),
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            **kwargs
        )

    def compile_report(self):
        """ Takes the outputs from all agents and combines them into a structured report. """
        
        return crewai.Task(
            description=dedent(f"""
                You have received **detailed assessments from various experts** analyzing an athlete's performance.  
                               
                **You have access to the full discussion history and analysis from all agents.**
                Use this information to **synthesize all the findings** into a **comprehensive and structured report**  
                that is **readable, insightful, and actionable**.                

                **Your report should include:**
                - **Executive Summary**: A high-level overview of key insights.
                - **Biomechanics Analysis**: Summary of movement efficiency and technique improvements.
                - **Conditioning Plan**: Breakdown of strength and endurance training.
                - **Motivation & Mental Resilience**: Psychological strategies to enhance focus and performance.
                - **Nutrition & Recovery**: Meal planning and dietary recommendations.
                - **Injury Prevention & Physiology**: Advice on preventing injuries and improving endurance.
                - **Position-Specific Coaching**: Tactical improvements based on the athlete’s role.
                
                **professional, structured, and formatted for easy reading**.
            """),
            agent=self,
            expected_output="A professionally formatted comprehensive report summarizing all agent insights."
        )
