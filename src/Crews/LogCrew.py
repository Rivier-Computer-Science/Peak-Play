import crewai
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from src.Agents.agent_helpers import concatente_task_outputs


class LogCrew:
    def __init__(self, player_data: str):
        self.player_data = StringKnowledgeSource(content=player_data)

    def run(self, task_id: str):
        # Initialize agents with file input
        athlete_profile_agent = ConditioningCoachAgent(athlete_profile=self.player_data)
        conditioning_coach_agent = ConditioningCoachAgent()
        motivator_agent = MotivatorAgent()

        agents = [
            athlete_profile_agent,
            conditioning_coach_agent,
            motivator_agent
        ]

        tasks = [
            athlete_profile_agent.provide_athlete_profile(),
            conditioning_coach_agent.generate_report(),
            motivator_agent.motivate_athlete()
        ]

        # Run tasks
        crew = crewai.Crew(
            agents=agents,
            tasks=tasks,
            knowledge_sources=[self.player_data],
            process=crewai.Process.sequential,
            verbose=True
        )

        result = crew.kickoff()       
        return concatente_task_outputs(result)