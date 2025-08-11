#######################################################################
# Agents
# - BlogTopicAgent: Select sport and topic
# - BlogWriterAgent: Write the blog post and improve it based on critique
# - BlogCriticAgent: Critique the blog post
# - BlogValidationAgent: Fact-check and fix
# - BlogPublisherAgent: Final packaging
#######################################################################

from __future__ import annotations

import datetime as dt
import json
import re
import math
from textwrap import dedent
from typing import List, Optional, Dict

import crewai as crewai
from pydantic import BaseModel

from src.Agents.base_agent import BaseAgent
from src.AgentTools.search_wikipedia import search_wikipedia
from src.AgentTools.search_unsplash_images import search_unsplash_images
from src.Helpers.sports_list import BLOG_SUMMER_SPORTS, BLOG_WINTER_SPORTS
import src.Helpers.writing_guidelines as wg

import src.Models.llm_config as llm_config


# ---------------------------------------------------------------------
# Global Prompts
# ---------------------------------------------------------------------
GUARD_RAILS = wg.GUARD_RAILS
QUALITY_BAR = wg.QUALITY_BAR
WRITING_GUIDELINES = wg.WRITING_GUIDELINES
BANNED_WORDS = wg.BANNED_WORDS
BANNED_PHRASES = wg.BANNED_PHRASES

# Consistent target length used throughout tasks
LENGTH_OF_BLOG_POST = "4000 to 5000 words"

# JSON example aligned with Pydantic schema below
JSON_FORMAT = dedent("""
{
  "success": "true",
  "result": {
    "post_title": "A short and descriptive blog title",
    "post_content": "Detailed Markdown content **WITHOUT** repeating the title...",
    "sport": "The sport (e.g., Fencing, Archery, etc.)",
    "post_tags": ["tag-one", "tag-two", "tag-three"]
  },
  "change_log": ["revisions made to blog post"]
}
""").strip()

# Percentage plan for blog post sections
P = {
    "hook":           (0.04,  0.05),
    "why_now":        (0.075, 0.08),
    "fundamentals":   (0.045, 0.05),
    "tech1":          (0.075, 0.08),
    "tech2":          (0.075, 0.08),
    "drills":         (0.11,  0.13),
    "plan4w":         (0.11,  0.13),
    "mistakes":       (0.06,  0.07),
    "recovery":       (0.06,  0.07),
    "mindset":        (0.045, 0.05),
    "gear":           (0.035, 0.04),
    "case":           (0.06,  0.07),
    "faq":            (0.06,  0.07),
    "takeaways":      (0.035, 0.04),
    "sources":        (0.01,  0.02),
}

def get_min_max_words():
    # Compute concrete word ranges from LENGTH_OF_BLOG_POST like "2000 to 3000 words"
    rng = re.findall(r'\d+', str(LENGTH_OF_BLOG_POST))
    if len(rng) >= 2:
        min_words, max_words = int(rng[0]), int(rng[1])
    elif len(rng) == 1:
        center = int(rng[0])
        min_words, max_words = math.floor(center * 0.85), math.ceil(center * 1.15)
    else:
        min_words, max_words = 2000, 3000

    return min_words, max_words

def get_blog_post_structure(min_words, max_words):
    """Computes the word count ranges for each section of the blog post."""
    def w(min_pct: float, max_pct: float) -> str:
        """Render a 'N–M words' range from percentage band."""
        lo = math.floor(min_words * min_pct)
        hi = math.floor(max_words * max_pct)
        return f"{lo}–{hi}"

    return dedent(f"""
        **Target Length**
        Aim for **{min_words}–{max_words} words** total in `post_content`.

        **Target Structure (use H2 `##` for each main section)**
        Provide these sections in order. Word ranges are computed as a percentage of the total target:
        1) ## Hook & Promise — {w(*P["hook"])} words (~4–5% of total)
        2) ## Why It Matters Now — {w(*P["why_now"])} words (~7.5–8%)
        3) ## Fundamentals in One Minute — {w(*P["fundamentals"])} words (~4.5–5%) — define key terms/jargon
        4) ## Core Technique #1 — {w(*P["tech1"])} words (~7.5–8%) — clear steps + cues
        5) ## Core Technique #2 — {w(*P["tech2"])} words (~7.5–8%) — clear steps + cues
        6) ## Drills & Progressions — {w(*P["drills"])} words (~11–13%) — numbered drills; sets/reps, rest, coaching cues
        7) ## Week-by-Week Plan (4 Weeks) — {w(*P["plan4w"])} words (~11–13%) — table or bullets: session goals, duration, intensity
        8) ## Common Mistakes & Fixes — {w(*P["mistakes"])} words (~6–7%) — bullet pairs: mistake → fix
        9) ## Recovery, Nutrition & Safety — {w(*P["recovery"])} words (~6–7%) — include one-sentence general-information disclaimer
        10) ## Mindset & Motivation — {w(*P["mindset"])} words (~4.5–5%) — practical routines
        11) ## Gear / Equipment Checklist — {w(*P["gear"])} words (~3.5–4%) — must-have vs nice-to-have
        12) ## Case Study or Scenario — {w(*P["case"])} words (~6–7%) — concrete example with numbers/dates if sensible
        13) ## Quick FAQ — {w(*P["faq"])} words (~6–7%) total across 3–5 Q&A items
        14) ## Key Takeaways — {w(*P["takeaways"])} words (~3.5–4%) — 5–8 bullets, 1–2 lines each
        15) ## Sources & Further Reading — cite 4–8 credible links (league/official, governing bodies, peer-reviewed, or vetted encyclopedias)
    """)


# ---------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------
class BlogSportAndTopic(BaseModel):
    sport: str
    topic: str


class BlogPostResult(BaseModel):
    post_title: str
    post_content: str
    sport: str
    post_tags: List[str]


class BlogPostOutput(BaseModel):
    success: str
    result: BlogPostResult
    change_log: List[str]



# ---------------------------------------------------------------------
# Base agent with LLM selection
# ---------------------------------------------------------------------
class BlogBaseAgent(BaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, llm: crewai.LLM, **kwargs):
        # Extract required parameters
        role : str = kwargs.pop('role', None)
        goal : str = kwargs.pop('goal', None)
        backstory: str = kwargs.pop('backstory', None)
        llm = llm
        kwargs.pop('llm', None)  #Remove it from kwargs

        # Ensure required arguments are provided
        if role is None or goal is None or backstory is None:
            raise ValueError(
                f"Error: Missing one of ['role', 'goal', 'backstory']. "
                f"Received: role={role}, goal={goal}, backstory={backstory}"
            )

        super().__init__(
            name=kwargs.pop('name', None),
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
        )


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
            {QUALITY_BAR}

            Guardrails:
            {GUARD_RAILS}
        """).strip()

        super().__init__(
            role=kwargs.pop('role', role),
            goal=kwargs.pop('goal', goal),
            backstory=kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

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
            output_json=BlogSportAndTopic,
            expected_output="A sport and a topic in JSON format"
        )


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
            • Transform a given **sport + topic** into a single, in-depth, {LENGTH_OF_BLOG_POST} article.  
            • Write in an engaging, supportive style that resonates with amateur athletes.  
            • Insert Unsplash images (0–3) **with exact photographer + Unsplash credit**; skip images if attribution cannot be verified.  
            • Guarantee every post is delivered as a valid JSON object that matches `BlogPostOutput`.
        """).strip()

        backstory = dedent(f"""
            You've spent 20+ years crafting research-informed sports articles that help amateurs elevate their game.
            Cite or link claims to authoritative sources (official leagues and governing bodies, peer-reviewed work when applicable, or verified encyclopedia entries).
            Include a short non-advice note for nutrition/health content when relevant.

            **Writing Guidelines (full)**
            {WRITING_GUIDELINES}

            {QUALITY_BAR}

            Guardrails:
            {GUARD_RAILS}

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
        min_words, max_words = get_min_max_words()

        base = dedent(f"""
            **Mission**
            Draft a brand-new blog post about the provided **sport** and **topic** for amateur athletes.
            Use only Markdown in `post_content` (no title there).

            {get_blog_post_structure(min_words, max_words)}

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
            output_json=BlogPostOutput,
            expected_output=f"A {LENGTH_OF_BLOG_POST} JSON blog post with Markdown content"
        )



    def revise_blog_post(self):
        min_words, max_words = get_min_max_words()

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
            • Your original and current goal is {LENGTH_OF_BLOG_POST}
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
            output_json=BlogPostOutput,
            expected_output=f"An enhanced {LENGTH_OF_BLOG_POST} JSON blog post and concise change log"
        )



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
            • Evaluate each draft for length ({LENGTH_OF_BLOG_POST}), structure, clarity, tone, grammar, and accessibility.  
            • Verify all Unsplash images include exact photographer + URL attribution; flag any missing or fabricated credits.  
            • Ensure the content serves amateur athletes, and when relevant, para/special-population athletes.  
            • Deliver concise, prioritized recommendations suitable for one revision cycle.
        """).strip()

        backstory = dedent(f"""
            You are an exacting but supportive editor. You harden arguments, improve flow, and keep tone constructive.

            **Writing Guidelines (full)**
            {WRITING_GUIDELINES}

            {QUALITY_BAR}

            Guardrails:
            {GUARD_RAILS}

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
            1) **Length** — {LENGTH_OF_BLOG_POST}; flag if outside range.  
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
            output_json=BlogPostOutput,
            expected_output="1) Corrected blog post JSON, 2) Markdown Change Log with key fixes"
        )


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
              - Word count remains {LENGTH_OF_BLOG_POST}.  
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
            {QUALITY_BAR}

            Guardrails:
            {GUARD_RAILS}
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
            {JSON_FORMAT}
        """)
        return crewai.Task(
            description=wg.with_guardrails(base, include_quality_bar=True),
            agent=self,
            output_json=BlogPostOutput,
            expected_output=dedent(f"""{JSON_FORMAT}""")
        )
