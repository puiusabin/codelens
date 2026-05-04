# agents/tester.py
import ollama

def generate_tests(code_content: str, analysis_context: str, framework: str = "pytest") -> str:
    """Agent 2: Generates unit tests based on the code and Agent 1's analysis."""
    
    system_prompt = f"""
    You are an expert QA Automation Engineer. 
    Write comprehensive unit tests for the provided code using {framework}.
    
    CRITICAL INSTRUCTIONS:
    1. Read the 'Analysis Context' to understand edge cases.
    2. Write tests for the 'happy path'.
    3. Write tests for exceptions. If testing an exception in Pytest, you MUST use `with pytest.raises(ExceptionType):`.
    4. Output ONLY raw, executable Python code. DO NOT wrap the code in markdown blocks (no ```python). DO NOT add explanations.
    """
    
    user_prompt = f"Code to test:\n{code_content}\n\nAnalysis Context:\n{analysis_context}"
    
    response = ollama.chat(
        model='gemma2',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    
    # Strip markdown formatting just in case Gemma ignores the prompt
    content = response['message']['content'].strip()
    if content.startswith('```python'):
        content = content[9:]
    elif content.startswith('```'):
        content = content[3:]
    if content.endswith('```'):
        content = content[:-3]
        
    return content.strip()