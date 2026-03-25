import anthropic
from app.config import settings
from sqlalchemy.orm import Session
from app.models import Lead, Employee, Company

def generate_pitch(industry: str, company_size: str, job_title: str, problem: str, intent_score: float) -> str:
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key or api_key == "your_anthropic_api_key_here":
        # Safe fallback
        return (
            f"Observation: Saw you are a {job_title} in the {industry} industry.\n"
            f"Problem: It seems your main priority right now is: {problem}.\n"
            f"Solution: Our intelligence platform can streamline this process.\n"
            f"Example: We recently helped a similar company of size {company_size} double their pipeline.\n"
            f"CTA: Would you be open to a quick chat next week?"
        )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""
        You are an expert SDR writing a highly personalized cold email. 
        Write a strict 5-part email without any other text or conversational filler.
        Structure:
        1. Observation
        2. Problem
        3. Solution
        4. Example use case
        5. CTA (book a demo)
        
        Context:
        - Lead Job Title: {job_title}
        - Industry: {industry}
        - Company Size: {company_size}
        - Detected Problem: {problem}
        - Intent Score (0-100): {intent_score} (determine urgency)
        
        Make it sound human, concise, and professional.
        """
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error generating pitch with Claude: {e}")
        return "Error generating pitch. Please check API key/connection."

def process_lead_pitch(db: Session, lead_id: int):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
        
    employee = db.query(Employee).filter(Employee.employee_id == lead.employee_id).first()
    company = db.query(Company).filter(Company.company_id == lead.company_id).first()
    
    if employee and company:
        pitch = generate_pitch(
            industry=company.industry or "Unknown",
            company_size=company.company_size or "Unknown",
            job_title=employee.job_title or "Unknown",
            problem=lead.problem or "Pipeline optimization",
            intent_score=lead.intent_score or 0.0
        )
        lead.pitch = pitch
        db.commit()
        db.refresh(lead)
        
    return lead
