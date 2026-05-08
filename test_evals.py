# test_evals.py
import ast

import pytest

from agents.analyzer import analyze_code, explain_code
from agents.tester import generate_tests

# We use a custom marker so we don't accidentally run heavy LLM tests in normal CI/CD


@pytest.mark.eval
def test_eval_agent1_catches_zero_division():
    """Eval: Does Agent 1 successfully identify a missing zero-division check?"""

    # 1. Arrange: A known vulnerable piece of code
    vulnerable_code = """
def calculate_average(total_sum, count):
    return total_sum / count
"""

    # 2. Act: Ask Gemma to analyze it
    result = analyze_code(vulnerable_code)
    result_lower = result.lower()

    # 3. Assert: Check if the LLM caught the specific code smell
    assert "zero" in result_lower or "0" in result_lower, "Agent 1 missed the ZeroDivision concept."
    assert "division" in result_lower or "error" in result_lower, "Agent 1 did not flag it as an error."


@pytest.mark.eval
def test_eval_agent2_writes_exception_test():
    """Eval: Does Agent 2 write tests for edge cases based on context?"""

    # 1. Arrange: Provide code AND a simulated warning from Agent 1
    code = """
def calculate_average(total_sum, count):
    return total_sum / count
"""
    context = "WARNING: Potential ZeroDivisionError if count is 0."

    # 2. Act: Ask Gemma to generate tests
    test_output = generate_tests(code, context, framework="pytest")

    # 3. Assert: Check if it actually wrote an exception test
    assert "def test_" in test_output, "Agent 2 did not generate a valid test function."
    assert "pytest.raises" in test_output, "Agent 2 ignored the edge case and did not write an exception test."
    assert "ZeroDivisionError" in test_output, "Agent 2 did not test for the specific error."


@pytest.mark.eval
def test_eval_agent2_output_is_valid_python():
    """Eval: Does Agent 2 generate syntactically valid Python code?"""
    code = """
def calculate_average(total_sum, count):
    return total_sum / count
"""
    context = "WARNING: Potential ZeroDivisionError if count is 0."
    test_output = generate_tests(code, context, framework="pytest")
    try:
        ast.parse(test_output)
    except SyntaxError as e:
        pytest.fail(f"Agent 2 generated syntactically invalid Python: {e}")


@pytest.mark.eval
def test_eval_agent1_identifies_sql_injection():
    """Eval: Does Agent 1 identify a SQL injection vulnerability?"""
    vulnerable_code = """
def get_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return db.execute(query)
"""
    result = analyze_code(vulnerable_code)
    result_lower = result.lower()
    assert "sql" in result_lower or "injection" in result_lower, \
        "Agent 1 missed the SQL injection vulnerability."
    assert "security" in result_lower or "vulnerability" in result_lower or "unsafe" in result_lower, \
        "Agent 1 did not flag it as a security issue."


@pytest.mark.eval
def test_eval_agent1_explain_has_required_sections():
    """Eval: Does explain_code produce TL;DR, Major Components, and Logic Flow sections?"""
    code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""
    result = explain_code(code)
    result_lower = result.lower()
    assert "tl;dr" in result_lower or "tldr" in result_lower, \
        "explain_code missing TL;DR section."
    assert "major components" in result_lower or "component" in result_lower, \
        "explain_code missing Major Components section."
    assert "logic flow" in result_lower or "logic" in result_lower, \
        "explain_code missing Logic Flow section."
