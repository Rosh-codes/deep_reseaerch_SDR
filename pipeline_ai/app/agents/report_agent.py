import anthropic
import json
from app.config import settings
from app.models import Lead, Company, Employee

def get_claude_client():
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key or api_key == "your_anthropic_api_key_here":
        return None
    return anthropic.Anthropic(api_key=api_key)

def generate_company_intelligence(company: Company) -> str:
    client = get_claude_client()
    if not client: return "API Key not configured. Please add ANTHROPIC_API_KEY."
    
    # Live duckduckgo scraping for factual accuracy
    web_context = "No recent live news found."
    media_context = ""
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        
        # Combine company name and industry for a highly targeted query
        query = f"{company.company_name} {company.industry} news growth hiring"
        results = ddgs.text(query, max_results=4)
        if results:
            web_context = "Recent Live Web Search Results:\n"
            for r in results:
                web_context += f"- Title: {r.get('title', '')}\n  Snippet: {r.get('body', '')}\n  Link: {r.get('href', '')}\n\n"
                
        # Scrape Live Internet Images
        img_results = ddgs.images(f"{company.company_name} corporate logo high quality", max_results=1)
        if img_results and 'image' in img_results[0]:
            media_context += f"![{company.company_name} Logo]({img_results[0]['image']})\n\n"
            
        prod_results = ddgs.images(f"{company.company_name} software interface graph platform", max_results=1)
        if prod_results and 'image' in prod_results[0]:
            media_context += f"![{company.company_name} Platform]({prod_results[0]['image']})\n\n"
            
    except Exception as e:
        pass
    
    prompt = f"""
    Generate a highly detailed "Company Intelligence Report" for {company.company_name}.
    Make it professional and structured. Use Markdown formatting.
    
    Static Company Context:
    - Name: {company.company_name}
    - Industry: {company.industry}
    - Company Size: {company.company_size}
    - Purchasing Frequency: {company.purchasing_frequency}
    
    Live Web Context (Use this to provide factual, up-to-date analysis!):
    {web_context}
    
    Sections Required:
    1. Company Overview (What they do, business model based on web results)
    2. Recent News & Growth Signals (Summarize the Live Web Context, provide the actual source Links as references!)
    3. Target Customers (Who they serve, B2B/B2C)
    4. Problem Identification (Likely sales, marketing, and scaling pain points based on their current growth state)
    5. Opportunity for Outreach (Why a pipeline/SaaS automation solution is relevant to them right now)
    """
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return media_context + msg.content[0].text
    except Exception as e:
        return f"Error connecting to Claude: {str(e)}"

def generate_outreach_strategy(lead: Lead, company: Company, employee: Employee) -> str:
    client = get_claude_client()
    if not client: return "API Key not configured."
    
    prompt = f"""
    Generate an "Outreach Strategy Plan" for this specific lead on behalf of our Pipeline Automation tool.
    Use Markdown. Make it highly strategic, realistic and professional.
    
    Target Lead Context:
    - Name: {employee.name}
    - Job Title: {employee.job_title}
    - Company Industry: {company.industry} 
    - Company Size: {company.company_size}
    - Calculated Intent Score: {lead.intent_score} (Range 0-100)
    
    Required bullet points:
    * Lead Priority (e.g. High/Medium/Low based on the Intent Score)
    * Why this lead is a good target
    * Their likely pain point
    * Recommended outreach angle
    * Recommended sequence strategy (e.g. Cold/Warm/Hot based on Intent)
    * Follow-up strategy
    * Best send time
    * Recommended communication channel
    * Risk level (Low/Medium/High)
    * Estimated reply probability (0-100%)
    * Estimated meeting booking probability (0-100%)
    """
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=800,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_email_variants(lead: Lead, company: Company, employee: Employee) -> dict:
    client = get_claude_client()
    if not client: return {"error": "API Key not configured."}
    
    prompt = f"""
    Generate 3 distinct, highly personalized cold emails for this lead selling our Pipeline/Automation product.
    Target: {employee.name}, {employee.job_title} at an {company.industry} company (Size: {company.company_size}).
    Detected Problem context: {lead.problem}
    
    Do NOT output JSON. Output EXACTLY 4 XML tags containing your responses:
    <email_a>
    (Problem-focused version)
    </email_a>
    
    <email_b>
    (ROI-focused version)
    </email_b>
    
    <email_c>
    (Case-study focused version)
    </email_c>
    
    <recommendation>
    (A brief sentence recommending which email to use and why.)
    </recommendation>
    """
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=900,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        content = msg.content[0].text
        import re
        def extract_tag(content, tag):
            match = re.search(f'<{tag}>(.*?)</{tag}>', content, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else "Error generating this variant."
            
        return {
            "email_a_problem": extract_tag(content, "email_a"),
            "email_b_roi": extract_tag(content, "email_b"),
            "email_c_case_study": extract_tag(content, "email_c"),
            "recommendation": extract_tag(content, "recommendation")
        }
    except Exception as e:
        return {"error": f"Failed to generate: {str(e)}"}

def generate_pipeline_report(funnel_metrics: dict) -> str:
    client = get_claude_client()
    if not client: return "API Key not configured."
    
    metrics_str = json.dumps(funnel_metrics, indent=2)
    prompt = f"""
    You are a Revenue Operations leader. Based on these pipeline metrics, generate a comprehensive "Pipeline Report".
    Use professional Markdown structuring.
    
    Current Pipeline Metric Inputs:
    {metrics_str}
    
    Sections:
    1. Pipeline Performance (Summary of the funnel volumes)
    2. Conversion Rates (Detailed breakdown of throughput)
    3. Best Performing Segments (Assess the top Industries, Roles, and Sequences provided)
    4. Where leads drop off (Identify the biggest bottleneck in the funnel)
    5. Recommendations to improve demo bookings
    6. Recommendations to improve demo attendance
    """
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"
