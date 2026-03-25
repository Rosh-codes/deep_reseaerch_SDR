import anthropic
import json
import re
from app.config import settings

def parse_user_query(query: str) -> dict:
    """
    Uses Claude Haiku to extract ONLY the single most important filter from a natural language query.
    Designed to be lenient and return broad matches rather than zero results.
    """
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key or api_key == "your_anthropic_api_key_here":
        return {} 

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""
You are a search filter extractor. Given the user's query, extract AT MOST ONE OR TWO filters.
DO NOT over-extract. Only extract what the user EXPLICITLY asks for.

Output a JSON object with AT MOST these keys:
- "keyword": A single broad word that captures the user's core need (e.g., "finance", "support", "marketing", "hiring", "automation")

ONLY add "industry" if the user explicitly names an industry sector.
ONLY add "job_title" if the user explicitly names a job role.
Do NOT invent filters the user didn't ask for.

CRITICAL: Output ONLY raw JSON. No markdown. No explanation.

Examples:
Query: "find companies in the finance field" -> {{"keyword": "finance"}}
Query: "companies that need customer support" -> {{"keyword": "support"}}
Query: "SaaS companies with a Head of Sales" -> {{"industry": "SaaS", "job_title": "Sales"}}
Query: "who needs AI automation" -> {{"keyword": "automation"}}

User Query: "{query}"
"""
        
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=100,
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
