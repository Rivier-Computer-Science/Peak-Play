from textwrap import dedent
from typing import List
import pydantic as pydantic

import crewai as crewai

from src.AgentTools.search_wikipedia import search_wikipedia
from src.AgentTools.search_unsplash_images import search_unsplash_images

from src.Agents.BlogAgents.blog_base_agent import BlogBaseAgent
import src.Agents.BlogAgents.blog_pydantic_definitions as pydantic_defs
import src.Agents.BlogAgents.blog_writing_guidelines as wg

LENGTH_OF_BLOG_POST = wg.LENGTH_OF_BLOG_POST
QUALITY_BAR = wg.QUALITY_BAR
GUARD_RAILS = wg.GUARD_RAILS

# ---------------------------------------------------------------------
# Blog Validation (Fact-check & compliance)
# ---------------------------------------------------------------------
class BlogValidationAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Blog-Post Fact-Checker & Validator for an athletic-performance website.
        """

        goal = dedent(f"""
            • Detect and eliminate hallucinations, inaccurate claims, or outdated data.  
            • Verify that every external link is live, relevant, and points to an authoritative source; fix or remove dead links.  
            • Confirm Unsplash images have **exact “Photo by <Photographer> on Unsplash”** attribution + working URL; correct or delete any that do not.  
            • Deliver a fully corrected article in valid `BlogPostOutput` JSON, plus a concise change log for transparency.
        """).strip()

        backstory = dedent(f"""
            You are the final factual backstop. You cross-check stats and claims against authoritative sources
            (official leagues, governing bodies, and peer-reviewed work when applicable).
            Preserve author voice; change only what is necessary for accuracy/compliance.
            {QUALITY_BAR}

            Guardrails:
            {GUARD_RAILS}

            Style enforcement (summary):
            - Ensure no semicolons or em dashes; no banned words/phrases remain; average sentence length is reasonable.
            - Use the StyleCheck tool and revise content as needed before finalizing output.
            - Do not enforce on URLs, image credits, or JSON keys/values.
        """).strip()

        super().__init__(
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            tools=[search_wikipedia, search_unsplash_images, wg.style_check],
            **kwargs
        )

    def validate_blog_post(self):
        base = dedent(f"""
            **Mission**  
            Audit the draft blog post provided in context and return a fully corrected version.

            **Validation Checklist**  
            1) **Facts & Figures** — corroborate every statistic or claim with reputable sources (league/official sites, governing bodies, peer-reviewed work; verified encyclopedia if needed).  
            2) **External Links** — ensure each URL is reachable and relevant; replace dead links with a valid equivalent or remove them.  
            3) **Image Credits** — Unsplash photos must carry the exact “Photo by <Photographer> on Unsplash” credit plus working URL.  
            4) **Word Count** — keep the final article in the {LENGTH_OF_BLOG_POST} range after edits.  
            5) **Voice** — preserve the author's tone and structure; change only what is necessary for accuracy and compliance.  
            6) **Markdown** — ensure the article only contains valid Markdown; avoid literal "\\n" sequences; use real Markdown line breaks.
            7) **StyleCheck (required)** — run the StyleCheck tool; if violations exist (semicolons, em dashes, banned tokens), correct them before final output.

            **Output**  
            Return **two elements** in this order:  
            1) A single JSON object that satisfies the `BlogPostOutput` schema, containing the fully corrected article.  
            2) A Markdown section titled `### Change Log` with bullet-point notes explaining every significant correction (≤ 10 bullets), including a `style_compliance` line.
            
            Do **not** output any other text.
        """)
        return crewai.Task(
            description=wg.with_style(wg.with_guardrails(base, include_quality_bar=True)),
            agent=self,
            output_json=pydantic_defs.BlogPostOutput,
            expected_output="1) Corrected blog post JSON, 2) Markdown Change Log with key fixes"
        )

