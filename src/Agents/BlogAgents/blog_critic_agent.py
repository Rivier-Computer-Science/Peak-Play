from textwrap import dedent

import crewai as crewai

from src.Agents.BlogAgents.blog_base_agent import BlogBaseAgent
import src.Agents.BlogAgents.blog_writing_guidelines as wg


# ---------------------------------------------------------------------
# Blog Critic
# ---------------------------------------------------------------------
class BlogCriticAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Blog-Post Quality Critic for an athletic-performance website.
        """

        goal = dedent(f"""
            • Evaluate each draft for length ({wg.LENGTH_OF_BLOG_POST}), structure, clarity, tone, grammar, and accessibility.  
            • Verify all Unsplash images include exact photographer + URL attribution; flag any missing or fabricated credits.  
            • Ensure the content serves amateur athletes, and when relevant, para/special-population athletes.  
            • Deliver concise, prioritized recommendations suitable for one revision cycle.
        """).strip()

        backstory = dedent(f"""
            You are an exacting but supportive editor. You harden arguments, improve flow, and keep tone constructive.

            **Writing Guidelines (full)**
            {wg.WRITING_GUIDELINES}

            {wg.QUALITY_BAR}

            Guardrails:
            {wg.GUARD_RAILS}

            Scope exceptions for style enforcement:
            - Do not enforce style bans on URLs, image credit lines (“Photo by … on Unsplash”), or JSON keys/values.
        """).strip()

        super().__init__(
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            tools=[wg.style_check],
            **kwargs
        )

    def critique_blog_post(self):
        base = dedent(f"""
            **Mission**  
            Critically review the draft blog post you receive as context.

            **Evaluation Checklist**  
            1) **Length** — {wg.LENGTH_OF_BLOG_POST}; flag if outside range.  
            2) **Structure** — logical flow; skimmable sub-headings; strong intro & clear takeaways.  
            3) **Clarity & Style** — engaging voice for amateurs; jargon explained; grammar/spelling correct.  
            4) **Images** — Unsplash photos properly credited; alt text meaningful; remove/replace faulty images.  
            5) **SEO & Tags** — clear title ≤ 60 chars, slug-worthy; tags relevant and do **not** duplicate the sport.  
            6) **Accuracy & Citations** — facts plausible; no unverified claims or plagiarism.  
            7) **StyleCheck (required)** — run the StyleCheck tool; list any style violations and advise concrete fixes.

            **Output**  
            Return bullet-point feedback under exactly these Markdown headings:

            ### Strengths
            - ...

            ### Issues
            - ...  (include any **Style Violations** here with counts and examples)

            ### Recommended Actions
            - ...  (include specific fixes for any style violations)
        """)
        return crewai.Task(
            description=wg.with_style(wg.with_guardrails(base, include_quality_bar=True)),
            agent=self,
            expected_output="A Markdown critique with Strengths / Issues / Recommended Actions sections"
        )

