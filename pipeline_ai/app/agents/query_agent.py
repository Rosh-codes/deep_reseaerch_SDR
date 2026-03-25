import anthropic
import json
from app.config import settings

def parse_user_query(query: str) -> dict:
    """
    Uses Claude Haiku (fast retrieval model) to extract structured DB filters from NL query.
    """
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key or api_key == "your_anthropic_api_key_here":
        return {} # Safe fallback returns empty filters

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""
        You are an AI data retrieval agent querying a SQLite database of leads.
        Extract the target criteria from the user's natural language query into a strict JSON format.
        Available fields:
        - industry (string, e.g. 'B2B SaaS', 'Fintech', 'Marketing Agency', 'Recruitment', 'E-commerce Brand')
        - company_size (string, e.g. 'Large', 'Medium', 'Small')
        - job_title (string, e.g. 'Head of Sales', 'VP', 'Founder', 'CFO')

        If a field is not mentioned, exclude it from the JSON completely.
        DO NOT return any other text besides the raw JSON object. Never include markdown markers.
        
        User Query: "{query}"
        """
        
        message = client.messages.create(
            model="claude-3-haiku-20240307", # Smaller model for instant routing
            max_tokens=150,
            temperature=0.0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        result = message.content[0].text.strip()
        if result.startswith("```json"):
            result = result[7:-3]
        elif result.startswith("```"):
            result = result[3:-3]
            
        return json.loads(result)
    except Exception as e:
        print(f"Error parsing query: {e}")
        return {}
