import pydantic as pydantic
import datetime as dt
from textwrap import dedent

import crewai as crewai

from src.Agents.BlogAgents.blog_base_agent import BlogBaseAgent
import src.Agents.BlogAgents.blog_pydantic_definitions as pydantic_defs
from src.Helpers.sports_list import BLOG_SUMMER_SPORTS, BLOG_WINTER_SPORTS
import src.Agents.BlogAgents.blog_writing_guidelines as wg
import src.Utils.utils as utils

#TODO: Can perhaps delete these from the prompts
# wg.GUARD_RAILS
# wg.QUALITY_BAR

# ---------------------------------------------------------------------
# Blog Topic Selector
# ---------------------------------------------------------------------
class BlogTopicAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Blog-Topic Selector for an athletic-performance website.
        """

        goal = dedent(f"""
            • Uniformly sample **one** sport from a list of sports.
              - If today's month in {dt.datetime.today()} is December through March, use {BLOG_WINTER_SPORTS}; otherwise use {BLOG_SUMMER_SPORTS}.
            • Propose **exactly one** specific, non-repeating topic for that sport.
            • Topic scope may span performance tips, nutrition, conditioning, skill drills, strategy, psychology, or motivation—but keep to a single focused idea.
        """).strip()

        backstory = dedent(f"""
            You are a veteran athletic analyst who curates timely, high-signal topics that resonate with middle school and older athletes.
            You avoid redundancy and saturated angles, favoring fresh, credible storylines.
            {wg.QUALITY_BAR}

            Guardrails:
            {wg.GUARD_RAILS}
        """).strip()

        super().__init__(
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )
        self.logger = utils.configure_logger()

    def select_blog_topic(self):
        base = dedent(f"""
            Today is {dt.datetime.today()}

            **Goal**  
            Propose a fresh blog post idea—*one sport + one specific topic*—for an audience of middle school and older.

            **Memory Check**  
            • Load your long-term memory of previous posts (sports + topics).  
            • Do **not** repeat any sport-topic pair that already exists.

            **Selection Rules**  
            1) Choose a sport using a true **uniform random draw** from {BLOG_WINTER_SPORTS} if the month is Dec–Mar, otherwise from {BLOG_SUMMER_SPORTS}.  
            2) Within the chosen sport, craft a concise, engaging topic that has **not** appeared before.  
            3) With *~15% probability*, tailor the topic to athletes with special considerations (e.g., para-athletes, left-handed players, visually impaired athletes). Otherwise, target the general population.

            **Output**  
            Return exactly one JSON object with fields {{ "sport": <str>, "topic": <str> }} — no extra text.
        """)
        return crewai.Task(
            description=wg.with_guardrails(base),
            agent=self,
            output_json=pydantic_defs.BlogSportAndTopic,
            expected_output="A sport and a topic in JSON format"
        )