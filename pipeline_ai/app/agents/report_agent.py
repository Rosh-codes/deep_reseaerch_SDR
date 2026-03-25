import anthropic
import json
import re
from datetime import datetime
from app.config import settings
from app.models import Lead, Company, Employee

def get_claude_client():
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key or api_key == "your_anthropic_api_key_here":
        return None
    return anthropic.Anthropic(api_key=api_key)


def _scrape_website(url: str) -> str:
    """Directly scrape a company's website for live content."""
    if not url or url == 'nan':
        return ""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Remove scripts and styles
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        # Limit to first 2000 chars to stay within token budget
        return text[:2000]
    except Exception as e:
        return f"Could not scrape website: {str(e)}"


# ══════════════════════════════════════════════
# MAIN: Chain Workflow Intelligence Report
# Step 1: Dataset Intelligence (verified data)
# Step 2: Live Website Scrape (requests+bs4)
# Step 3: Claude Analysis & Reasoning
# ══════════════════════════════════════════════
def generate_company_intelligence(company: Company) -> str:
    client = get_claude_client()
    if not client: return "API Key not configured. Please add ANTHROPIC_API_KEY."
    
    current_date = datetime.now().strftime("%B %d, %Y")
    name = company.company_name or "Unknown"
    
    # ── Chain Step 1: Live Website Scrape ──
    website_content = _scrape_website(company.website_url)
    
    prompt = f"""
You are a world-class Sales Intelligence Analyst generating a "Company Intelligence Report".
Today's date is: {current_date}.

══════════════════════════════════
VERIFIED DATABASE INTELLIGENCE:
- Company Name: {name}
- Industry: {company.industry}
- Website: {company.website_url}
- Country: {company.country}
- Company Size: {company.company_size}
- What they do: {company.description}
- Known challenges: {company.why_needs_help}
- Suggested outreach angle: {company.outreach_angle}

LIVE WEBSITE SCRAPE ({company.website_url}):
{website_content}
══════════════════════════════════

Generate a comprehensive, data-driven report with these sections:

# Company Intelligence Report: {name}
**Report Date:** {current_date} | **Website:** {company.website_url}

## 1. Executive Summary
(One paragraph combining database intel and live website data)

## 2. Company Overview
(What they do, their products/services, business model. Use BOTH the database description AND the live website content.)

## 3. Market Position & Size
(Industry: {company.industry}, Size: {company.company_size}, Country: {company.country})

## 4. Live Website Analysis
(Summarize key insights from the website scrape — what products/features they highlight, their messaging, target audience)

## 5. Identified Pain Points
(Based on BOTH the known challenges AND website analysis, determine their specific operational/sales/growth pains)

## 6. What This Business Needs
(Recommend specific solutions/tools they would likely buy based on pain points)

## 7. Outreach Opportunity
(Why contacting them NOW makes sense. Reference: {company.outreach_angle})

Be specific, cite the data, and use professional Markdown formatting.
"""
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4000,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error connecting to Claude: {str(e)}"


def generate_outreach_strategy(lead: Lead, company: Company, employee: Employee) -> str:
    client = get_claude_client()
    if not client: return "API Key not configured."
    
    current_date = datetime.now().strftime("%B %d, %Y")
    name = company.company_name or "Unknown"
    
    prompt = f"""
You are a top-tier SDR strategist. Generate an "Outreach Strategy Plan".
Today's date: {current_date}

Target Lead:
- Name: {employee.name}
- Job Title: {employee.job_title}
- Company: {name} ({company.website_url})
- Industry: {company.industry}
- Company Size: {company.company_size}
- Intent Score: {lead.intent_score}/100
- Known Pain Point: {company.why_needs_help}
- Recommended Angle: {company.outreach_angle}

Generate in Markdown:
1. **Lead Priority Assessment** (High/Medium/Low with reasoning)
2. **Why This Lead Is a Good Target** (specific to their role and company needs)
3. **Their Specific Pain Points** (from the known pain point data)
4. **Recommended Outreach Angle** (informed by the suggested angle)
5. **Sequence Strategy** (Cold/Warm/Hot with day-by-day cadence)
6. **Communication Channel Recommendation** (Email/LinkedIn/Phone)
7. **Risk Assessment** (Low/Medium/High)
8. **Estimated Reply Probability** (0-100%)
9. **Estimated Meeting Booking Probability** (0-100%)
"""
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_email_variants(lead: Lead, company: Company, employee: Employee) -> dict:
    client = get_claude_client()
    if not client: return {"error": "API Key not configured."}
    
    name = company.company_name or "Unknown"
    
    prompt = f"""
Generate 3 distinct cold emails selling our AI-powered Sales Automation product.
Target: {employee.name}, {employee.job_title} at {name} ({company.industry}).
Their need: {company.why_needs_help}
Angle: {company.outreach_angle}

Do NOT output JSON. Output EXACTLY 4 XML tags:
<email_a>
(Problem-focused email — reference their specific pain point)
</email_a>

<email_b>
(ROI-focused email — quantify potential business impact)
</email_b>

<email_c>
(Case-study focused email — reference a similar company success)
</email_c>

<recommendation>
(Which email to use and why)
</recommendation>
"""
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        content = msg.content[0].text
        
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
You are a Revenue Operations leader. Generate a concise "Pipeline Report" in Markdown.

Metrics:
{metrics_str}

Sections:
1. Pipeline Performance Summary
2. Conversion Rate Breakdown
3. Top Performing Segments
4. Biggest Bottleneck
5. Actionable Recommendations
"""
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1500,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"
