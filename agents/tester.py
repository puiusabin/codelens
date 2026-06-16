# agents/tester.py
import ast

from agents import llm


def generate_tests(code_content: str, analysis_context: str, framework: str = "pytest") -> str:
    """Agent 2: Generates unit tests based on the code and Agent 1's analysis."""

    system_prompt = f"""
    You are an expert QA Automation Engineer.
    Write {framework} unit tests for the provided Python code.

    RULES:
    1. Import pytest and import every function you test at the top.
    2. Every test function MUST be named starting with def test_.
    3. Organize tests into two sections with these exact headers:
       # --- Happy Path Tests ---
       # --- Edge Case Tests ---
    4. Write a # WHY: comment above every test explaining what it verifies.
    5. Use pytest.raises() for any test that expects an exception.
    6. Output ONLY raw Python code. No markdown fences. No explanation text.

    Example output format:
    import pytest
    from mymodule import my_func

    # --- Happy Path Tests ---
    # WHY: Verifies the normal case returns the correct value.
    def test_my_func_basic():
        assert my_func(2, 3) == 5

    # --- Edge Case Tests ---
    # WHY: Verifies empty input raises ValueError.
    def test_my_func_empty():
        with pytest.raises(ValueError):
            my_func([])
    """

    user_prompt = f"Code to test:\n{code_content}\n\nAnalysis Context:\n{analysis_context}"

    # Strip markdown fences in case the model ignores the prompt
    content = llm.chat(system_prompt, user_prompt).strip()
    if content.startswith('```python'):
        content = content[9:]
    elif content.startswith('```'):
        content = content[3:]
    if content.endswith('```'):
        content = content[:-3]
    content = content.strip()

    # Strip trailing prose — stop only when the remaining content both parses
    # and contains at least one test function. A bare comment parses cleanly
    # but has no tests, so the old "any valid Python" check stopped too early.
    lines = content.splitlines()
    while lines:
        joined = '\n'.join(lines)
        try:
            ast.parse(joined)
            if 'def test_' in joined:
                break
        except SyntaxError:
            pass
        lines.pop()
    return '\n'.join(lines).strip()
