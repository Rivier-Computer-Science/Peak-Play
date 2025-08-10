from rich.console import Console
from rich.table import Table
import json
import src.Models.llm_config as llm_config

def _get_cached_prompt_tokens(usage: dict) -> int:
    """
    Try multiple known shapes to find cached prompt tokens.
    Returns 0 if not present.
    """
    # OpenAI-style nested details
    details = usage.get("prompt_tokens_details")
    if isinstance(details, dict):
        val = details.get("cached_tokens")
        if isinstance(val, int):
            return max(val, 0)

    # Other possible keys surfaced by SDKs/adapters
    for key in ("cached_prompt_tokens", "cached_tokens", "cached_input_tokens", "cache_hit_tokens"):
        val = usage.get(key)
        if isinstance(val, int):
            return max(val, 0)

    return 0


def display_crew_output(crew_output, llm=llm_config.GPT5MiniConfig()):
    console = Console()

    # If crew_output is a JSON string, parse it
    if isinstance(crew_output, str):
        try:
            crew_output = json.loads(crew_output)
        except json.JSONDecodeError:
            console.print("[bold red]Error:[/bold red] crew_output is a string and not valid JSON.")
            console.print(f"[bold yellow]Raw Output:[/bold yellow] {crew_output}")
            return

    # Per-token prices (you said you already divided by 1M)
    INPUT_TOKEN_COST         = llm.get_input_cost()
    CACHED_INPUT_TOKEN_COST  = llm.get_cached_input_cost()
    OUTPUT_TOKEN_COST        = llm.get_output_cost()

    # Raw Output
    if getattr(crew_output, "raw", None):
        console.print(f"[bold yellow]Raw Output:[/bold yellow] {crew_output.raw}\n")

    # JSON Output
    if getattr(crew_output, "json_dict", None):
        console.print("[bold underline]JSON Output:[/bold underline]")
        console.print(json.dumps(crew_output.json_dict, indent=2))

    # Pydantic Output
    if getattr(crew_output, "pydantic", None):
        console.print("\n[bold underline]Pydantic Output:[/bold underline]")
        console.print(crew_output.pydantic_output)

    # Tasks Output
    console.print("\n[bold underline]Tasks Output:[/bold underline]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Description", style="cyan", overflow="fold")
    table.add_column("Summary", style="green", overflow="fold")
    table.add_column("Raw Output", style="white", overflow="fold")
    table.add_column("Agent", style="yellow")
    table.add_column("Output Format", style="red")

    for task in getattr(crew_output, "tasks_output", []):
        table.add_row(
            (task.description or "").strip(),
            (task.summary or "").strip(),
            (task.raw or "").strip(),
            getattr(task, "agent", "") or "",
            getattr(task, "output_format", getattr(task, "output_format", "")).value if getattr(task, "output_format", None) else ""
        )
    console.print(table)

    # Token Usage
    console.print("\n[bold underline]Token Usage:[/bold underline]")
    usage_table = Table(show_header=True, header_style="bold blue")
    usage_table.add_column("Metric", style="dim")
    usage_table.add_column("Value", justify="right")

    # Convert UsageMetrics to dict before iterating
    token_usage = getattr(crew_output, "token_usage", None)
    token_usage_dict = token_usage.dict() if hasattr(token_usage, "dict") else (token_usage or {})
    if not isinstance(token_usage_dict, dict):
        token_usage_dict = {}

    # Retrieve token counts
    prompt_tokens     = int(token_usage_dict.get("prompt_tokens", 0) or 0)
    completion_tokens = int(token_usage_dict.get("completion_tokens", 0) or 0)
    total_tokens      = int(token_usage_dict.get("total_tokens", prompt_tokens + completion_tokens) or 0)

    # Cached prompt tokens (may be nested under prompt_tokens_details.cached_tokens)
    cached_prompt_tokens = _get_cached_prompt_tokens(token_usage_dict)
    # Ensure we don't exceed total prompt tokens
    cached_prompt_tokens = min(cached_prompt_tokens, prompt_tokens)
    uncached_prompt_tokens = max(prompt_tokens - cached_prompt_tokens, 0)

    # Calculate costs (per token)
    input_cost_uncached = uncached_prompt_tokens * INPUT_TOKEN_COST
    input_cost_cached   = cached_prompt_tokens * CACHED_INPUT_TOKEN_COST
    input_cost_total    = input_cost_uncached + input_cost_cached
    output_cost         = completion_tokens * OUTPUT_TOKEN_COST
    total_cost          = input_cost_total + output_cost

    # Add raw token usage rows first (as-is from the object)
    for key, value in token_usage_dict.items():
        # pretty label
        label = key.replace("_", " ").capitalize()
        if isinstance(value, dict):
            # print nested dicts as JSON to avoid crashing the table
            value = json.dumps(value)
        usage_table.add_row(label, str(value))

    # Add derived rows (make it clear these are computed)
    usage_table.add_row("Cached prompt tokens (derived)", f"{cached_prompt_tokens}")
    usage_table.add_row("Uncached prompt tokens (derived)", f"{uncached_prompt_tokens}")

    # Add the calculated costs
    usage_table.add_row("Input token cost (uncached, USD)", f"${input_cost_uncached:.6f}")
    usage_table.add_row("Input token cost (cached, USD)",   f"${input_cost_cached:.6f}")
    usage_table.add_row("Input token cost (total, USD)",    f"${input_cost_total:.6f}")
    usage_table.add_row("Output token cost (USD)",          f"${output_cost:.6f}")
    usage_table.add_row("Total estimated cost (USD)",       f"${total_cost:.6f}")

    console.print(usage_table)
