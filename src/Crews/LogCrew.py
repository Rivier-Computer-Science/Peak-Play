import crewai
from src.Agents.conditioning_coach_agent import ConditioningCoachAgent
from src.Agents.motivator_agent import MotivatorAgent
from src.Agents.agent_helpers import concatente_task_outputs
from src.Helpers.athlete_profile import AthleteProfile


class LogCrew:
    def __init__(self, athlete_data):
        self.athlete_data = AthleteProfile(athlete_data)

    def run(self, task_id: str):
        # Initialize agents with file input
        athlete_profile_agent = ConditioningCoachAgent(athlete_profile=self.athlete_data)
        conditioning_coach_agent = ConditioningCoachAgent(athlete_profile=self.athlete_data)
        motivator_agent = MotivatorAgent(athlete_profile=self.athlete_data)

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
            process=crewai.Process.sequential,
            verbose=True
        )

        result = crew.kickoff()       
        return concatente_task_outputs(result)