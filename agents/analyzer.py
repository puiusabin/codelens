# agents/analyzer.py
import ollama
import yaml
from pathlib import Path


def _load_project_instructions() -> str:
    yaml_path = Path.cwd() / "codelens.yaml"
    if not yaml_path.exists():
        return ""
    data = yaml.safe_load(yaml_path.read_text())
    return data.get("instructions", "") if data else ""


def _chat(system_prompt: str, user_content: str) -> str:
    extra = _load_project_instructions()
    full_prompt = f"{system_prompt}\n\n{extra}".strip() if extra else system_prompt
    response = ollama.chat(
        model='gemma2',
        messages=[
            {'role': 'system', 'content': full_prompt},
            {'role': 'user', 'content': user_content},
        ]
    )
    return response['message']['content']


def chat_response(messages: list[dict]) -> str:
    """Agent 1: One turn in a multi-turn conversation."""
    response = ollama.chat(model='gemma2', messages=messages)
    return response['message']['content']


def analyze_code(code_content: str) -> str:
    """Agent 1: General analysis — used as context for the test command."""
    system_prompt = """
    You are an expert Senior Software Engineer.
    Review the following code. Provide a short TL;DR,
    explain the main logic, and list any code smells or security issues.
    Format your response in Markdown.
    """
    return _chat(system_prompt, f"Here is the code to analyze:\n\n{code_content}")


def explain_code(code_content: str) -> str:
    """Agent 1: Structured explanation for the explain command."""
    system_prompt = """
    You are an expert Senior Software Engineer doing a code review.
    Analyze the following code and respond with EXACTLY these sections in Markdown:

    ## TL;DR
    One or two sentences summarizing what this code does.

    ## Major Components
    A bullet list of the key functions, classes, or modules and what each does.

    ## Logic Flow
    A step-by-step description of how the code executes from entry to exit.
    """
    return _chat(system_prompt, f"Code to analyze:\n\n{code_content}")


def check_code_smells(code_content: str) -> str:
    """Agent 1: Code smell detection with severity and line numbers."""
    system_prompt = """
    You are a security-focused Senior Software Engineer.
    Analyze the following code ONLY for code smells, bugs, and security issues.
    For each issue found, output a line in EXACTLY this format:
    [WARNING] Line <N>: <description>
    or
    [CRITICAL] Line <N>: <description>
    Use [CRITICAL] for security vulnerabilities, potential crashes, and data loss risks.
    Use [WARNING] for code smells, bad practices, and maintainability issues.
    If no issues are found, output: No issues found.
    Output ONLY these lines. No explanations, no preamble.
    """
    return _chat(system_prompt, f"Code to check:\n\n{code_content}")


def analyze_diff(diff_content: str) -> str:
    """Agent 1: Analyzes a GitHub PR diff."""
    system_prompt = """
    You are an expert Senior Software Engineer reviewing a Pull Request.
    Analyze the following git diff and respond with EXACTLY these sections in Markdown:

    ## Summary of Changes
    What this PR does in 2-3 sentences.

    ## Key Changes
    A bullet list of the most significant changes.

    ## Potential Impact
    Risks, breaking changes, or areas that need careful review.
    """
    return _chat(system_prompt, f"PR Diff to review:\n\n{diff_content}")
