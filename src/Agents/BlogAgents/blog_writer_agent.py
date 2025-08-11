from textwrap import dedent
from typing import List
import pydantic as pydantic

import crewai as crewai

from src.AgentTools.search_wikipedia import search_wikipedia
from src.AgentTools.search_unsplash_images import search_unsplash_images

from src.Agents.BlogAgents.blog_base_agent import BlogBaseAgent
import src.Agents.BlogAgents.blog_pydantic_definitions as pydantic_defs
import src.Agents.BlogAgents.blog_writing_guidelines as wg


# ---------------------------------------------------------------------
# Blog Writer
# ---------------------------------------------------------------------
class BlogWriterAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Primary Blog-Post Author for an athletic-performance website.
        """

        goal = dedent(f"""
            • Transform a given **sport + topic** into a single, in-depth, {wg.LENGTH_OF_BLOG_POST} article.  
            • Write in an engaging, supportive style that resonates with amateur athletes.  
            • Insert Unsplash images (0–3) **with exact photographer + Unsplash credit**; skip images if attribution cannot be verified.  
            • Guarantee every post is delivered as a valid JSON object that matches `BlogPostOutput`.
        """).strip()

        backstory = dedent(f"""
            You've spent 20+ years crafting research-informed sports articles that help amateurs elevate their game.
            Cite or link claims to authoritative sources (official leagues and governing bodies, peer-reviewed work when applicable, or verified encyclopedia entries).
            Include a short non-advice note for nutrition/health content when relevant.

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
            tools=[search_wikipedia, search_unsplash_images, wg.style_check],
            **kwargs
        )

    def write_blog_post(self):
        min_words, max_words = wg.get_min_max_words()

        base = dedent(f"""
            **Mission**
            Draft a brand-new blog post about the provided **sport** and **topic** for amateur athletes.
            Use only Markdown in `post_content` (no title there).

            {wg.get_blog_post_structure(min_words, max_words)}

            **Style & Tone**
            • Informative, supportive, and memorable for amateur readers.
            • Define jargon on first use; avoid clichés and filler.

            **Evidence & Links**
            • Link claims to credible sources (official stats, governing bodies, peer‑reviewed work where applicable, or verified encyclopedia entries).
            • Do **not** fabricate citations.

            **Images (optional)**
            • 0–3 Unsplash images total; first image (if any) appears at the top.
            • Each image MUST include exact credit: “Photo by <Photographer> on Unsplash” plus a working URL.
            • If the topic centers on para‑athletes or special populations, images must depict that group—or omit images.

            **Sensitive Content**
            • If nutrition/health appears, include a brief non‑advice disclaimer and avoid personalized directives.

            **Length Enforcement**
            • Ensure `post_content` falls within **{min_words}–{max_words} words**.
            • If total < {min_words}, expand Sections 6, 7, 8, and 13 first; if still short, expand 2 and 12.
            • If total > {max_words}, compress Sections 2, 9, and 10 (keep clarity and evidence).

            **Style Check (required)**
            • Call the StyleCheck tool on your draft content (title + headings + body + captions + alt text).
            • If any violations are flagged (banned tokens, semicolons, em dashes), revise until they are zero.
            • Aim for ~20–30 words per sentence on average; reduce sentences >30 words.

            **Output**
            Return a *single* JSON object complying with `BlogPostOutput`.
            Do **NOT** include the title inside `post_content`.
            In `change_log`, add:
            - `style_compliance: {{semicolons:0, em_dashes:0, banned_tokens_fixed:N}}`
            - `word_count: <approx total words in post_content>`
            - `sections: 15`
        """)

        return crewai.Task(
            description=wg.with_style(wg.with_guardrails(base, include_quality_bar=True)),
            agent=self,
            output_json=pydantic_defs.BlogPostOutput,
            expected_output=f"A {wg.LENGTH_OF_BLOG_POST} JSON blog post with Markdown content"
        )



    def revise_blog_post(self):
        min_words, max_words = wg.get_min_max_words()

        base = dedent(f"""
            **Mission**
            You are revising the prior draft using the **BlogCriticAgent** feedback provided in context
            under `### Strengths`, `### Issues`, and `### Recommended Actions`. Produce an updated article
            that preserves the original thesis and audience while implementing the critic’s guidance.            

            **Integrating Critic Feedback**
            - Treat **Recommended Actions** as must‑fix unless they conflict with guardrails or verifiable facts.
            - If a recommendation conflicts, keep the safer/factual option and add a one‑line `skipped:` note in `change_log` explaining why.
            - Address explicit calls to expand, compress, reorder, add citations, fix tone, or adjust SEO/headings.
            - Do not invent new facts; add or replace with credible sources when support is requested.

            **Style & Tone**
            • Informative, supportive, memorable; define jargon on first use; avoid clichés and filler.

            **Evidence & Links**
            • Link claims to credible sources (official stats, governing bodies, peer‑reviewed work where applicable, or verified encyclopedia entries).
            • Do **not** fabricate citations.

            **Images (optional)**
            • 0–3 Unsplash images total; first image (if any) appears at the top.
            • Each image MUST include: “Photo by <Photographer> on Unsplash” + working URL.
            • If the topic centers on para‑athletes or special populations, images must depict that group—or omit images.

            **Sensitive Content**
            • If nutrition/health appears, include a brief non‑advice disclaimer and avoid personalized directives.

            **Length Enforcement**
            • Your original and current goal is {wg.LENGTH_OF_BLOG_POST}
            • If total < {min_words}, expand Sections 6, 7, 8, and 13 first; then 2 and 12 if still short.
            • If total > {max_words}, compress Sections 2, 9, and 10 (preserve clarity and evidence).

            **Style Check (required)**
            • Run the StyleCheck tool on the revised content (title + headings + body + captions + alt text).
            • Eliminate violations (banned tokens, semicolons, em dashes) and target ~20–30 words/sentence; split >30‑word sentences.

            **Output**
            Return a *single* JSON object that satisfies `BlogPostOutput`.
            Do **NOT** include the title inside `post_content`.
            Update `change_log` with concise past‑tense bullets including:
            - `style_compliance: {{semicolons:0, em_dashes:0, banned_tokens_fixed:N}}`
            - `word_count: <approx total words in post_content>`
            - `sections: 15`
            - `critic_applied: <brief list of implemented actions>`
            - Any `skipped:` items with one‑line reasons.
        """)
        return crewai.Task(
            description=wg.with_style(wg.with_guardrails(base, include_quality_bar=True)),
            agent=self,
            output_json=pydantic_defs.BlogPostOutput,
            expected_output=f"An enhanced {wg.LENGTH_OF_BLOG_POST} JSON blog post and concise change log"
        )

