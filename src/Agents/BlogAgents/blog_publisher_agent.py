from textwrap import dedent

import crewai as crewai

from src.Agents.BlogAgents.blog_base_agent import BlogBaseAgent
import src.Agents.BlogAgents.blog_pydantic_definitions as pydantic_defs
import src.Agents.BlogAgents.blog_writing_guidelines as wg

# ---------------------------------------------------------------------
# Blog Publisher (final packaging)
# ---------------------------------------------------------------------
class BlogPublisherAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Final-Stage Publisher & Copy-Editor for an athletic-performance blog.
        """

        goal = dedent(f"""
            • Integrate all upstream edits (Writer, Critic, Validator) into a polished, SEO-ready article.  
            • Verify:  
              - Word count remains {wg.LENGTH_OF_BLOG_POST}.  
              - No “insert here” or placeholder text survives.  
              - Images: first image **at the top**; up to two others spaced logically; Unsplash credits intact.  
              - Title ≤ 60 characters; slug-friendly.  
              - `post_tags` are relevant single-word/slug phrases **excluding** the sport name.  
            • Output a single JSON object that matches `BlogPostOutput` **exactly**, with no extra text.
        """).strip()

        backstory = dedent(f"""
            For 25+ years you have been the last pair of eyes on high-traffic sports blogs, combining
            precision copy-editing with layout savvy. You harmonize multiple contributors' edits
            while guaranteeing zero publication-blocking errors.
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

    def publish_blog_post(self):
        base = dedent(f"""
            **Mission**  
            Conduct a final quality-assurance pass on the draft blog post provided in context.
            Implement any edits necessary to meet the “Goal” spec above.

            **Output Requirements**  
            1) Return *only* a JSON object that conforms **exactly** to the schema.  
            2) Do **NOT** wrap the JSON in backticks or Markdown; no explanatory prose.

            Example schema (shape only; fill with your final values):
            {wg.JSON_FORMAT}
        """)
        return crewai.Task(
            description=wg.with_guardrails(base, include_quality_bar=True),
            agent=self,
            output_json=pydantic_defs.BlogPostOutput,
            expected_output=dedent(f"""{wg.JSON_FORMAT}""")
        )
