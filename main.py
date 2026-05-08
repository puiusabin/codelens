# main.py
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from pathlib import Path

from agents.analyzer import analyze_code, explain_code, check_code_smells, analyze_diff, chat_response
from agents.github_api import fetch_pr_diff
from agents.tester import generate_tests
from config import save_config, load_config

app = typer.Typer(help="CodeLens: AI-Powered Code Review CLI")
console = Console()

VALID_BACKENDS = ["openai", "anthropic", "ollama"]

auth_app = typer.Typer(help="Authentication commands.")
app.add_typer(auth_app, name="auth")


@app.command()
def init():
    """Prompts for AI backend and saves configuration to ~/.codelens_config."""
    backend = typer.prompt("Select AI backend (openai/anthropic/ollama)", default="ollama")
    if backend not in VALID_BACKENDS:
        console.print(
            f"[bold red]Error:[/bold red] Invalid backend '{backend}'. "
            f"Choose from: {', '.join(VALID_BACKENDS)}"
        )
        raise typer.Exit(code=1)
    save_config({"ai_backend": backend})
    console.print("[bold green]✓ Configuration saved to ~/.codelens_config[/bold green]")


@auth_app.command("github")
def auth_github():
    """Stores a GitHub Personal Access Token in ~/.codelens_config."""
    token = typer.prompt("Enter your GitHub Personal Access Token", hide_input=True)
    save_config({"github_token": token})
    console.print("[bold green]✓ GitHub token saved to ~/.codelens_config[/bold green]")


@app.command()
def explain(filepath: str):
    """Analyzes a local file and explains its logic."""
    path = Path(filepath)

    if not path.is_file():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    with console.status(f"[bold cyan]Reading {filepath}...", spinner="dots"):
        code_content = path.read_text()

    with console.status("[bold green]Agent 1 is analyzing the code...", spinner="bouncingBar"):
        explanation = explain_code(code_content)

    console.print("\n[bold yellow]--- CodeLens Analysis ---[/bold yellow]")
    console.print(Markdown(explanation))


@app.command()
def check(filepath: str):
    """Analyzes a file for code smells and security issues."""
    path = Path(filepath)

    if not path.is_file():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    code_content = path.read_text()

    with console.status("[bold cyan]Agent 1 is scanning for code smells...", spinner="dots"):
        smells = check_code_smells(code_content)

    console.print("\n[bold yellow]--- CodeLens Code Check ---[/bold yellow]")
    for line in smells.strip().splitlines():
        if line.startswith("[CRITICAL]"):
            console.print(f"[bold red]{line}[/bold red]")
        elif line.startswith("[WARNING]"):
            console.print(f"[bold yellow]{line}[/bold yellow]")
        else:
            console.print(line)


@app.command()
def review(pr_url: str):
    """Fetches a GitHub PR diff and analyzes the changes."""
    config = load_config()
    token = config.get("github_token")

    with console.status("[bold cyan]Fetching PR diff from GitHub...", spinner="dots"):
        try:
            diff = fetch_pr_diff(pr_url, token)
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[bold red]Error fetching PR:[/bold red] {e}")
            raise typer.Exit(code=1)

    with console.status("[bold green]Agent 1 is analyzing the PR...", spinner="bouncingBar"):
        analysis = analyze_diff(diff)

    console.print("\n[bold yellow]--- CodeLens PR Review ---[/bold yellow]")
    console.print(Markdown(analysis))


@app.command()
def chat(filepath: str):
    """Opens an interactive chat session about a file."""
    path = Path(filepath)
    if not path.is_file():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    code_content = path.read_text()
    system_prompt = (
        "You are an expert Senior Software Engineer. "
        "Answer questions about the following code concisely and specifically.\n\n"
        f"Code:\n{code_content}"
    )
    messages = [{'role': 'system', 'content': system_prompt}]

    console.print("[bold green]Chat mode active. Type 'exit' or 'quit' to leave.[/bold green]")

    while True:
        try:
            question = typer.prompt(">")
        except (EOFError, KeyboardInterrupt):
            break
        if question.strip().lower() in ("exit", "quit"):
            break

        messages.append({'role': 'user', 'content': question})

        with console.status("[bold cyan]Thinking...", spinner="dots"):
            answer = chat_response(messages)

        messages.append({'role': 'assistant', 'content': answer})
        console.print(Markdown(answer))


@app.command()
def test(filepath: str, framework: str = "pytest", save: bool = False):
    """Generates unit tests for a local file using Agent 1 (Analysis) and Agent 2 (QA)."""
    path = Path(filepath)

    if not path.is_file():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    code_content = path.read_text()

    with console.status("[bold cyan]Agent 1 is analyzing the code for edge cases...", spinner="dots"):
        analysis = analyze_code(code_content)

    with console.status(f"[bold green]Agent 2 is writing {framework} tests...", spinner="bouncingBar"):
        test_code = generate_tests(code_content, analysis, framework)

    console.print(f"\n[bold yellow]--- Generated {framework.capitalize()} Tests ---[/bold yellow]")
    console.print(Syntax(test_code, "python", theme="monokai", line_numbers=True))

    if save:
        test_filename = f"test_{path.name}"
        Path(test_filename).write_text(test_code)
        console.print(f"\n[bold green]✓ Tests successfully saved to {test_filename}[/bold green]")


if __name__ == "__main__":
    app()
