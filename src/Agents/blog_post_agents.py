#######################################################################
# Agents
# - BlogTopicAgent: Select sport and topic
# - BlogWriterAgent: Write the blog post and improve it based on critique
# - BlogCriticAgent: Critique the blog post
########################################################################

import crewai as crewai
from textwrap import dedent

from pydantic import BaseModel
from typing import List

from src.Agents.base_agent import BaseAgent
from src.AgentTools.search_wikipedia import search_wikipedia
from src.AgentTools.search_unsplash_images import search_unsplash_images

import src.Models.llm_config as llm_config


class BlogPostResult(BaseModel):
    post_title: str
    post_content: str
    sport:str
    post_tags: List[str]

class BlogPostOutput(BaseModel):
    success: str
    result: BlogPostResult

JSON_FORMAT="""
{
    "success": true,
    "result": {
        "post_title": "A short and descriptive blog title",
        "post_content": "Detailed markdown content **WITHOUT** the title..."
        "sport": "The sport (e.g., Fencing, Achery, etc.)"
        "post_tags": "A list of Wordpress tags but do not include the sport"
    }
}    
"""

class BlogBaseAgent(BaseAgent):
    role: str
    goal: str
    backstory: str
    
    def __init__(self, **kwargs):
       
        # Extract required parameters
        role = kwargs.pop('role', None)
        goal = kwargs.pop('goal', None)
        backstory = kwargs.pop('backstory', None)

        # Ensure required arguments are provided
        if role is None or goal is None or backstory is None:
            raise ValueError(f"Error: Missing one of ['role', 'goal', 'backstory']. Received: role={role}, goal={goal}, backstory={backstory}")
                
        super().__init__(
            name=kwargs.pop('name', None),
            role=role,
            goal=goal,
            backstory=backstory,
            llm=kwargs.pop('llm', llm_config.gpt_41_llm_blog_post),
        )

class BlogTopicAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Blog-Topic Selector for an athletic-performance website.
        """

        goal = """
            • Uniformly sample **one** sport from the global universe of sports.
            • Propose **exactly one** specific, non-repeating topic for that sport.
            • Topic scope may span performance tips, nutrition, conditioning, skill drills,
            strategy, psychology, or motivation—but never combine multiple topics.
        """

        backstory = """
            You are a veteran athletic analyst with decades of experience curating content
            that resonates with novice and intermediate athletes—male, female, para-athletes,
            and those with unique attributes (e.g., left-handed players). Your insight drives
            engaging, actionable blog posts that broaden the platform’s reach while avoiding
            redundancy.
        """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def select_blog_topic(self, age: str = '21'): 
        # Preprocessing goes here
        return crewai.Task(
            description = dedent("""
                **Goal**  
                Propose a fresh blog post idea— *one sport + one specific topic*—for an audience of middle school and older.

                **Memory Check**  
                • Load your long-term memory of previous posts (sports + topics).  
                • Do **not** repeat any sport-topic pair that already exists.

                **Selection Rules**  
                1. Choose a sport using a true **uniform random draw** from the master list `sports_list`.  
                – This ensures the same sport isn’t over-represented across runs.  
                2. Within the chosen sport, craft a concise, engaging topic that has **not** appeared before.  
                3. With *~15 % probability*, tailor the topic to athletes with special considerations  
                (e.g., para-athletes, left-handed players, visually impaired athletes). Otherwise, target the general athletic population.  

                **Output Format**  
                Return exactly one JSON object, no extra text:  
                ```json
                {
                "sport": "<Sport Name>",
                "topic": "<One-sentence topic, ≤ 20 words>"
                }
                ```
            """),
            agent=self,
            expected_output="A sport and a topic in JSON format"
        )  



class BlogWriterAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Primary Blog-Post Author for an athletic-performance website.
        """

        goal = """
            • Transform a given **sport + topic** into a single, in-depth, 1500 to 2000-word article.  
            • Write in an engaging, witty style that resonates with amateur athletes.  
            • Insert Unsplash images (or none) **with exact photographer + URL credit**.  
            • Guarantee every Markdown post is delivered as a JSON object that matches `BlogPostOutput`.
        """

        backstory = """
            You’ve spent 20 + years crafting memorable, research-driven sports articles that help amateurs
            elevate their game.  Your secret sauce is blending actionable advice with humor, science-based
            insight, and eye-catching imagery.  You champion inclusivity—whenever the assigned topic
            involves para-athletes or athletes with unique attributes (e.g., left-handed), you ensure the
            text *and* images reflect that audience authentically.
        """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[search_wikipedia, search_unsplash_images],
            **kwargs
        )

    def write_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(
                f"""
                **Mission**  
                Draft a brand-new blog post about the provided **sport** and **topic**.

                **Style & Tone**  
                • 1500 to 2000 words (≈ 11 to 14 min read).  
                • Informative, witty, and memorable.  
                • Assume an amateur-athlete reader.

                **Images**  
                • Optional Unsplash images are encouraged (1 to 3 max).  
                • For each image, embed Markdown like  
                  `![alt text](IMAGE_URL "Photo by PHOTOGRAPHER on Unsplash")`.  
                • Absolutely no fabricated credits; skip an image if you cannot verify real
                  attribution.  
                • If the article focuses on para-athletes or special populations, images must
                  depict that group—or omit images entirely.

                **Output**  
                Return a *single* JSON object complying with `BlogPostOutput`.  
                Do **NOT** include the title inside `post_content`.  
                
                Example format:
                {JSON_FORMAT}                

                """
            ),
            agent=self,
            output_json=BlogPostOutput,
            expected_output="A 1500 to 2000-word JSON blog post with Markdown content"
        )        

    def revise_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(
                """
                **Mission**  
                Improve the draft blog post based on critique notes you’ll receive as context.

                **Revision Checklist**  
                1. Tighten flow and clarity; preserve the original voice.  
                2. Add, remove, or swap Unsplash images to better support the text and comply
                   with attribution rules.  
                3. Ensure word count remains 1500 to 2000.  
                4. Validate JSON output matches the `BlogPostOutput` schema.

                **Output**  
                Return a single updated JSON object—same format as in the *write* task.
                """
            ),
            agent=self,
            output_json=BlogPostOutput,
            expected_output="An enhanced 1500 to 2000-word JSON blog post with Markdown content"
        )  


class BlogCriticAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Blog-Post Quality Critic for an athletic-performance website.
        """

        goal = """
            • Evaluate each draft for length (1500 to 2000 words), structure, clarity, tone, grammar, and inclusivity.  
            • Verify all Unsplash images include exact photographer + URL attribution; flag any missing or fabricated credits.  
            • Ensure the content serves amateur athletes, para-athletes, and special-population athletes when relevant.  
            • Deliver concise, prioritized recommendations the writer can implement in one revision cycle.
        """

        backstory = """
            You have spent two decades editing and critiquing sports-performance writing.  
            Your sharp eye for narrative flow, SEO-friendly structure, and reader engagement
            has boosted countless blogs from mediocre to must-read.  You balance rigorous
            standards with a constructive tone, always supplying clear next steps rather
            than vague criticisms.
        """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )

    def critique_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(
                """
                **Mission**  
                Critically review the draft blog post you receive as context.

                **Evaluation Checklist**  
                1. **Length** – 1500 to 2000 words; flag if outside range.  
                2. **Structure** – logical flow, skimmable sub-headings, strong intro & CTA.  
                3. **Clarity & Style** – engaging voice for amateurs; jargon explained; grammar/spelling correct.  
                4. **Inclusivity** – para-athlete or special-population focus handled authentically when applicable.  
                5. **Images** – Unsplash photos properly credited; alt text meaningful; remove/replace faulty images.  
                6. **SEO & Tags** – clear title ≤ 60 chars, slug-worthy; tags relevant and do **not** duplicate the sport.  
                7. **Accuracy & Citations** – facts plausible; no unverified claims or plagiarism.

                **Output**  
                Return bullet-point feedback under exactly these Markdown headings:  

                ```
                ### Strengths
                - ...

                ### Issues
                - ...

                ### Recommended Actions
                - ...
                ```

                Be specific and solution-oriented.  If the piece is too short, state the
                approximate deficit and suggest areas to expand.  Do **not** rewrite the
                article—focus on guidance the writer can apply.
                """
            ),
            agent=self,
            expected_output="A Markdown critique with Strengths / Issues / Recommended Actions sections"
        )      
    

class BlogValidationAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Blog-Post Fact-Checker & Validator for an athletic-performance website.
        """

        goal = """
            • Detect and eliminate hallucinations, inaccurate claims, or outdated data.  
            • Verify that every external link is live, relevant, and points to an authoritative source; fix or remove dead links (e.g., *example.com*).  
            • Confirm Unsplash images have **exact photographer + URL** attribution; correct or delete any that do not.  
            • Deliver a fully corrected article (1500 to 2000 words) in valid `BlogPostOutput` JSON, plus a concise change log for transparency.
        """

        backstory = """
            After twenty years as a sports-science editor and professional fact-checker,
            you have an eagle eye for misinformation in athletic-performance content.
            Your meticulous review process—cross-referencing peer-reviewed studies,
            reputable sports organizations, and encyclopedic sources—keeps readers
            safe from bogus advice while preserving the writer’s voice and flow.
        """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[search_wikipedia, search_unsplash_images],
            **kwargs
        )

    def validate_blog_post(self): 
        # Preprocessing goes here
        return crewai.Task(
            description=dedent(
                """
                **Mission**  
                Audit the draft blog post provided in context and return a fully
                corrected version.

                **Validation Checklist**  
                1. **Facts & Figures** – corroborate every statistic or claim with a
                   reputable source (e.g., ISSN-indexed journal, major sports
                   federation, or Wikipedia entry you’ve cross-checked).  
                2. **External Links** – ensure each URL is reachable and relevant;
                   replace dead links (e.g., *example.com*) with a valid equivalent
                   or remove them.  
                3. **Image Credits** – Unsplash photos must carry the exact
                   “Photo by <Photographer> on Unsplash” credit plus working URL.  
                4. **Word Count** – keep the final article in the 1 500–2 000-word
                   range after edits.  
                5. **Voice** – preserve the author’s tone and structure; change only
                   what is necessary for accuracy and compliance.

                **Output**  
                Return **two elements** in this order:  

                1. A single JSON object that satisfies the `BlogPostOutput` schema,
                   containing the fully corrected article.  
                2. A Markdown section titled `### Change Log` with bullet-point
                   notes explaining every significant correction (≤ 10 bullets).

                Do **not** output any other text.
                """
            ),
            agent=self,
            expected_output=(
                "1) Corrected blog post JSON, 2) Markdown Change Log with key fixes"
            ),
        )       
    

class BlogPublisherAgent(BlogBaseAgent):
    role: str
    goal: str
    backstory: str

    def __init__(self, **kwargs):
        role = """
            Final-Stage Publisher & Copy-Editor for an athletic-performance blog.
        """

        goal = """
            • Integrate all upstream edits (Writer, Critic, Validator) into a polished, SEO-ready article.  
            • Verify:  
            – Word count remains 1500 to 2000 words.  
            – No “insert here” or placeholder text survives.  
            – Images: first image at top; 1 to 3 others spaced logically; Unsplash credits intact; swap/remove if
                para-athlete focus isn’t reflected.  
            – Title ≤ 60 characters; slug-friendly.  
            – `post_tags` are relevant single-word/slug phrases **excluding** the sport name.  
            • Output a single JSON object that matches `BlogPostOutput` **exactly**, with no extra text.
        """

        backstory = """
            For 25+ years you have been the last pair of eyes on high-traffic sports blogs, combining
            precision copy-editing with layout savvy.  You excel at harmonizing multiple contributors’
            edits, enforcing brand style, and guaranteeing zero publication-blocking errors.
        """
    
        super().__init__(
            role = kwargs.pop('role', role),
            goal = kwargs.pop('goal', goal),
            backstory = kwargs.pop('backstory', backstory),
            tools=[],
            **kwargs
        )


    def publish_blog_post(self): 
        return crewai.Task(
            description=dedent(
                f"""
                **Mission**  
                Conduct a final quality-assurance pass on the draft blog post provided in context.
                Implement any edits necessary to meet the “Goal” spec above.

                **Output Requirements**  
                1. Return *only* a JSON object that conforms **exactly** to the schema shown below
                   (variable `JSON_FORMAT`).  
                2. Do **NOT** wrap the JSON in backticks or Markdown; no explanatory prose.

                {JSON_FORMAT}
                """
            ),
            agent=self,
            output_json=BlogPostOutput,
            expected_output=dedent(f""" {JSON_FORMAT}""")
        )
      