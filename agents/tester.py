# agents/tester.py
import ollama

def generate_tests(code_content: str, analysis_context: str, framework: str = "pytest") -> str:
    """Agent 2: Generates unit tests based on the code and Agent 1's analysis."""
    
    system_prompt = f"""
    You are an expert QA Automation Engineer. 
    Your task is to write comprehensive unit tests for the provided code using {framework}.
    
    CRITICAL INSTRUCTIONS:
    1. Read the provided 'Analysis Context' to understand the code smells and edge cases.
    2. Write tests for the 'happy path' (normal inputs).
    3. Write tests for the edge cases mentioned in the analysis (e.g., exceptions, invalid inputs).
    4. Output ONLY the code block containing the tests. Do not include introductory text.
    """
    
    user_prompt = f"Code to test:\n{code_content}\n\nAnalysis Context:\n{analysis_context}"
    
    response = ollama.chat(
        model='gemma2',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    
    return response['message']['content']