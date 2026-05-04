# main.py
import typer
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path

from agents.analyzer import analyze_code
from agents.tester import generate_tests

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

@app.command()
def test(filepath: str, framework: str = "pytest", save: bool = False):
    """
    Generates unit tests for a local file using Agent 1 (Analysis) and Agent 2 (QA).
    """
    path = Path(filepath)
    
    if not path.is_file():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    # 1. Read the file
    code_content = path.read_text()

    # 2. Run Agent 1 to get the context
    with console.status("[bold cyan]Agent 1 is analyzing the code for edge cases...", spinner="dots"):
        analysis = analyze_code(code_content)
        
    # 3. Run Agent 2 to generate the tests
    with console.status(f"[bold green]Agent 2 is writing {framework} tests...", spinner="bouncingBar"):
        test_code = generate_tests(code_content, analysis, framework)

    # 4. Output the results
    console.print(f"\n[bold yellow]--- Generated {framework.capitalize()} Tests ---[/bold yellow]")
    console.print(Markdown(test_code))

    # 5. Handle the --save flag
    if save:
        # Create a new filename, e.g., test_script.py -> test_test_script.py
        test_filename = f"test_{path.name}"
        Path(test_filename).write_text(test_code)
        console.print(f"\n[bold green]✓ Tests successfully saved to {test_filename}[/bold green]")

if __name__ == "__main__":
    app()