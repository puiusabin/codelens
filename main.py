# main.py
import typer
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
from agents.analyzer import analyze_code

# Initialize Typer and Rich Console
app = typer.Typer(help="CodeLens: AI-Powered Code Review CLI")
console = Console()

@app.command()
def explain(filepath: str):
    """
    Analyzes a local file and explains its logic.
    """
    path = Path(filepath)
    
    if not path.is_file():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    # Read the file
    with console.status(f"[bold cyan]Reading {filepath}...", spinner="dots"):
        code_content = path.read_text()

    # Call Agent 1 (Gemini)
    with console.status("[bold green]Agent 1 is analyzing the code...", spinner="bouncingBar"):
        explanation = analyze_code(code_content)

    # Print the result beautifully in the terminal
    console.print("\n[bold yellow]--- CodeLens Analysis ---[/bold yellow]")
    console.print(Markdown(explanation))

if __name__ == "__main__":
    app()