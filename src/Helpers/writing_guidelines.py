# Reusable prompts

from textwrap import dedent
import json
import re

WRITING_GUIDELINES = """
You are a human writer following comprehensive writing guidelines. Every sentence must adhere to these guidelines exactly.

POSITIVE DIRECTIVES (How you SHOULD write):
• Craft sentences that average 20-30 words and focus on a single idea
• Use active voice 90% of the time
• Substitute common, concrete words for abstraction
• Rely primarily on periods, commas, question marks, and occasional colons for lists
• Mix short and medium sentences; avoid stacking clauses
• Build arguments with plain connectors: 'and', 'but', 'so', 'then'
• Provide numbers, dates, names, and measurable facts whenever possible
• Vary paragraph length; ask genuine questions no more than once per 300 words

CRITICAL PROHIBITIONS (What you MUST NEVER use):
BANNED WORDS: however, moreover, furthermore, additionally, consequently, therefore, ultimately, generally, essentially, arguably, significant, innovative, efficient, dynamic, ensure, foster, leverage, utilize, cutting-edge, seamless, robust, holistic, paradigm, synergy, optimize, game-changer, unleash, uncover, elevate, embark, delve, tapestry, bustling, vibrant, realm, virtuoso, symphony, soul, crucible, enhance, emphasise, enable, revolutionize, folks, foster, labyrinthine, remnant, nestled, labyrinth, gossamer, enigma, whispering, metamorphosis, indelible

BANNED PHRASES: "At the end of the day", "With that being said", "It goes without saying", "In a nutshell", "Needless to say", "When it comes to", "Moving forward", "Going forward", "On the other hand", "As a matter of fact", "In the realm of", "In a world", "In a sea of", "Digital landscape", "In the midst", "In addition", "It's important to note", "Delve into", "In summary", "In conclusion", "Remember that", "Take a dive into", "Navigating the landscape", "In the world of", "Testament to", "Out of the box", "Hustle and bustle", "Dive into", "In today's digital era", "As previously mentioned", "It's worth noting that", "To summarize", "To put it simply", "In other words", "Both sides have merit", "Ultimately, the answer depends on", "This is not an exhaustive list", "Unlock the secrets of"

PROHIBITED PUNCTUATION: Never use semicolons (;) or em dashes (—)

FAILURE TO COMPLY WITH ANY PROHIBITION INVALIDATES THE OUTPUT.
""".strip()

GUARD_RAILS = dedent("""
- No profanity or masked profanity; no slurs, hate speech, harassment, or demeaning language.
- No sexual content; no self-harm facilitation; no instructions enabling illegal or unsafe activity.
- Constructive-only: if you flag a problem, offer a positive, safer alternative.
- Do not invent facts, quotes, or citations. If uncertain, say so and suggest how to verify. Prefer authoritative sources.
- Do not reveal or solicit PII about private individuals; redact PII in quoted text.
- Health/nutrition/legal/finance: provide high-level, evidence-informed info with a brief non-advice disclaimer; no personalized directives.
- Output hygiene: be clear, concise, and professional; no swearing; keep JSON valid when requested; do not reveal chain-of-thought.
""").strip()

QUALITY_BAR = dedent("""
- Accurate, current, and verifiable (no fabricated sources).
- Actionable, high-signal guidance for amateur athletes and coaches.
- Coherent structure with descriptive headings and skimmable sections.
- Style: energetic yet measured; avoid hype, clichés, and filler.
- Cite or link claims where appropriate; avoid plagiarism.
- Fully compliant with the guardrails above.
""").strip()

BANNED_WORDS = [
    "additionally",
    "arguably",
    "bustling",
    "consequently",
    "crucial",
    "crucible",
    "cutting-edge",
    "delve",
    "dynamic",
    "efficient",
    "elevate",
    "embark",
    "emphasise",
    "enable",
    "enhance",
    "enigma",
    "ensure",
    "essentially",
    "folks",
    "foster",
    "furthermore",
    "game-changer",
    "generally",
    "gossamer",
    "holistic",
    "however",
    "indelible",
    "innovative",
    "labyrinth",
    "labyrinthine",
    "leverage",
    "metamorphosis",
    "moreover",
    "nestled",
    "optimize",
    "paradigm",
    "realm",
    "remnant",
    "revolutionize",
    "robust",
    "seamless",
    "significant",
    "soul",
    "symphony",
    "synergy",
    "tapestry",
    "therefore",
    "ultimately",
    "uncover",
    "unleash",
    "utilize",
    "vibrant",
    "virtuoso",
    "whispering",
]


BANNED_PHRASES = [
    "as a matter of fact",
    "as previously mentioned",
    "at the end of the day",
    "both sides have merit",
    "delve into",
    "digital landscape",
    "dive into",
    "going forward",
    "hustle and bustle",
    "in a nutshell",
    "in a sea of",
    "in a world",
    "in addition",
    "in conclusion",
    "in other words",
    "in summary",
    "in the midst",
    "in the realm of",
    "in the world of",
    "in today's digital era",
    "it goes without saying",
    "it's important to note",
    "it's worth noting that",
    "moving forward",
    "navigating the landscape",
    "needless to say",
    "on the other hand",
    "out of the box",
    "remember that",
    "take a dive into",
    "testament to",
    "this is not an exhaustive list",
    "to put it simply",
    "to summarize",
    "ultimately, the answer depends on",
    "unlock the secrets of",
    "when it comes to",
    "with that being said",
]

# ---------------------------------------------------------------------
# Helper Functiions
# ---------------------------------------------------------------------
def with_guardrails(base: str, *, include_quality_bar: bool = False) -> str:
    """Append a compact guardrail/quality reminder to any Task description."""
    parts = [base, "**Guardrails (summary)**\n" + GUARD_RAILS]
    if include_quality_bar:
        parts.append("**Quality Bar**\n" + QUALITY_BAR)
    return "\n\n".join(parts)

def with_style(base: str) -> str:
    """Append a compact style reminder to any Task description (full policy lives in Writer & Critic backstories)."""
    style_summary = dedent("""
    **Style compliance (summary)**
    - Follow WRITING_GUIDELINES (sentence avg 20–30 words; 90% active voice; plain words; no semicolons or em dashes).
    - Do NOT use banned words/phrases listed in WRITING_GUIDELINES.
    - Scope: apply to title, headings, body, captions, and alt text; NOT to URLs, image credits, or JSON keys/values.
    - Use the StyleCheck tool on your draft; if violations are flagged, revise until violations are zero for punctuation and banned tokens.
    """).strip()
    return base + "\n\n" + style_summary

# ---------------------------------------------------------------------
# Lightweight StyleCheck tool (regex-based heuristic)
# Returns a JSON string with counts and flags so agents can decide to revise.
# NOTE: Not enforced on URLs, image credits, or JSON keys/values.
# ---------------------------------------------------------------------
def style_check(text: str) -> str:
    """
    StyleCheck tool:
    Input: plain text (title + headings + body + captions + alt text)
    Output: JSON string:
    {
      "semicolons": <int>,
      "em_dashes": <int>,
      "banned_words": ["..."],
      "banned_phrases": ["..."],
      "sentence_avg_words": <float>,
      "sentences_over_30": <int>,
      "passive_voice_hits": <int>,
      "ok": <bool>,
      "notes": ["..."]
    }
    """
    # Remove URLs and image credit lines from analysis to avoid false positives
    cleaned = re.sub(r'https?://\\S+', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'Photo by .* on Unsplash', '', cleaned, flags=re.IGNORECASE)

    semicolons = cleaned.count(';')
    em_dashes = cleaned.count('—')

    # Banned words (whole word, case-insensitive)
    bw_found = []
    for w in BANNED_WORDS:
        if re.search(rf'\\b{re.escape(w)}\\b', cleaned, flags=re.IGNORECASE):
            bw_found.append(w)

    # Banned phrases (substring match, case-insensitive)
    bp_found = []
    for p in BANNED_PHRASES:
        if re.search(re.escape(p), cleaned, flags=re.IGNORECASE):
            bp_found.append(p)

    # Sentence length (rough): split on . ! ?
    sentences = re.split(r'[.!?]+\\s+', cleaned.strip())
    sentences = [s for s in sentences if s]
    word_counts = [len(re.findall(r'\\b\\w+\\b', s)) for s in sentences] or [0]
    avg_words = sum(word_counts) / max(len(word_counts), 1)
    over_30 = sum(1 for n in word_counts if n > 30)

    # Passive voice heuristic: forms of "be" + past participle (very rough)
    passive_hits = len(re.findall(r'\\b(is|are|was|were|be|been|being)\\b\\s+\\w+ed\\b', cleaned, flags=re.IGNORECASE))

    # OK if no banned tokens and no forbidden punctuation and average length not extreme
    ok = (semicolons == 0 and em_dashes == 0 and not bw_found and not bp_found)

    notes = []
    if semicolons: notes.append(f"Found {semicolons} semicolon(s); replace with period or restructure.")
    if em_dashes: notes.append(f"Found {em_dashes} em dash(es); replace with colon or period.")
    if bw_found: notes.append(f"Banned words present: {sorted(set(bw_found))[:10]}{' ...' if len(set(bw_found))>10 else ''}.")
    if bp_found: notes.append(f"Banned phrases present: {sorted(set(bp_found))[:5]}{' ...' if len(set(bp_found))>5 else ''}.")
    if avg_words < 15 or avg_words > 30:
        notes.append(f"Average sentence length {avg_words:.1f} words (target ~20–30).")
    if over_30:
        notes.append(f"{over_30} sentence(s) exceed 30 words; split or tighten.")
    if passive_hits > len(sentences) * 0.2:
        notes.append("Passive voice may be high; prefer active voice.")

    return json.dumps({
        "semicolons": semicolons,
        "em_dashes": em_dashes,
        "banned_words": sorted(set(bw_found)),
        "banned_phrases": sorted(set(bp_found)),
        "sentence_avg_words": round(avg_words, 2),
        "sentences_over_30": over_30,
        "passive_voice_hits": passive_hits,
        "ok": ok,
        "notes": notes or ["No style issues detected."]
    })

