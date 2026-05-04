# agents/analyzer.py
import ollama

def analyze_code(code_content: str) -> str:
    """Agent 1: Explains the code and finds code smells using local Gemma."""
    
    system_prompt = """
    You are an expert Senior Software Engineer. 
    Review the following code. Provide a short TL;DR, 
    explain the main logic, and list any code smells or security issues.
    Format your response in Markdown.
    """
    
    # We use the ollama.chat interface to talk to the local gemma2 model
    response = ollama.chat(
        model='gemma2',
        messages=[
            {
                'role': 'system', 
                'content': system_prompt
            },
            {
                'role': 'user', 
                'content': f"Here is the code to analyze:\n\n{code_content}"
            }
        ]
    )
    
    # Extract and return the text content from Gemma's reply
    return response['message']['content']