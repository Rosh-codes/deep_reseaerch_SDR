import anthropic
import json
import re
from app.config import settings

def parse_user_query(query: str) -> dict:
    """
    Uses Claude Haiku (fast retrieval model) to extract structured DB filters from NL query.
    """
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key or api_key == "your_anthropic_api_key_here":
        return {} 

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""
        You are an AI data retrieval agent querying a database of business leads.
        Extract target criteria from the user's query into a STRICT JSON format.
        
        Available fields for the JSON mapping:
        - "industry": Map their request securely to broad standard terms if asked (e.g. 'SaaS', 'Fintech', 'Marketing', 'Ecommerce', 'Recruitment', 'Software', 'AI'). E.g., 'finance' -> 'Fintech'.
        - "company_size": Map to terms like 'Large', 'Medium', or 'Small'.
        - "job_title": Extract the target professional role (e.g. 'Sales', 'Growth', 'CEO').

        If the user mentions anything related to an industry, infer it accurately. 
        If a field is NOT determinable from the prompt, OMIT it from the JSON.
        
        CRITICAL RULES:
        1. OUTPUT ONLY THE RAW JSON DICT. NOT A SINGLE EXTRA WORD.
        2. NO MARKDOWN. NO CODE BLOCKS.
        
        Example outputs:
        {{"industry": "Fintech"}}
        {{"job_title": "Sales", "company_size": "Large"}}
        
        User Query: "{query}"
        """
        
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=150,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = message.content[0].text.strip()
        
        # Regex matching to forcibly extract the JSON blob if wrapped
        match = re.search(r'\{.*?\}', result, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}
    except Exception as e:
        print(f"Error parsing query: {e}")
        return {}
