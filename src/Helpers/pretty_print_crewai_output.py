from rich.console import Console
from rich.table import Table
import json

def display_crew_output(crew_output):
    console = Console()

    # Check if crew_output is a string, parse it if necessary
    if isinstance(crew_output, str):
        try:
            crew_output = json.loads(crew_output)
        except json.JSONDecodeError:
            console.print("[bold red]Error:[/bold red] crew_output is a string and not valid JSON.")
            console.print(f"[bold yellow]Raw Output:[/bold yellow] {crew_output}")
            return

    # GPT-4o pricing
    INPUT_TOKEN_COST = 2.5 / 1e6   # Cost per input token in USD
    OUTPUT_TOKEN_COST = 10.0 / 1e6 # Cost per output token in USD

    # Raw Output
    if crew_output.raw:
        console.print(f"[bold yellow]Raw Output:[/bold yellow] {crew_output.raw}\n")

    # JSON Output
    if crew_output.json_dict:
        console.print("[bold underline]JSON Output:[/bold underline]")
        console.print(json.dumps(crew_output.json_dict, indent=2))
    
    # Pydantic Output
    if crew_output.pydantic:
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
    
    for task in crew_output.tasks_output:
        table.add_row(
            task.description.strip(),
            task.summary.strip(),
            task.raw.strip(),
            task.agent,
            task.output_format.value
        )
    
    console.print(table)

    # Token Usage
    console.print("\n[bold underline]Token Usage:[/bold underline]")
    usage_table = Table(show_header=True, header_style="bold blue")
    usage_table.add_column("Metric", style="dim")
    usage_table.add_column("Value", justify="right")

    # Convert UsageMetrics to dict before iterating
    token_usage_dict = crew_output.token_usage.dict()

    # Retrieve token counts
    prompt_tokens = token_usage_dict.get('prompt_tokens', 0)
    completion_tokens = token_usage_dict.get('completion_tokens', 0)
    total_tokens = token_usage_dict.get('total_tokens', 0)

    # Calculate individual costs
    input_cost = prompt_tokens * INPUT_TOKEN_COST
    output_cost = completion_tokens * OUTPUT_TOKEN_COST
    total_cost = input_cost + output_cost

    # Add token usage rows
    for key, value in token_usage_dict.items():
        usage_table.add_row(key.replace("_", " ").capitalize(), str(value))

    # Add the calculated costs
    usage_table.add_row("Input token cost (USD)", f"${input_cost:.6f}")
    usage_table.add_row("Output token cost (USD)", f"${output_cost:.6f}")
    usage_table.add_row("Total estimated cost (USD)", f"${total_cost:.6f}")

    console.print(usage_table)