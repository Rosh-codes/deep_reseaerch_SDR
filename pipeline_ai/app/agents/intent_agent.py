from sqlalchemy.orm import Session
from app.models import Lead, Employee, Company

def calculate_intent_score(employee: Employee, company: Company) -> float:
    score = 0.0
    
    # 1. Seniority (Director/VP/C-Level = high score)
    seniority = (employee.seniority or "").lower()
    if any(title in seniority for title in ['c-level', 'ceo', 'cto', 'vp', 'director', 'founder', 'chief']):
        score += 20
    elif 'manager' in seniority or 'head' in seniority:
        score += 10
    else:
        score += 5

    # 2. Engagement score (higher = more intent)
    eng = employee.engagement_score or 0
    score += min(20, eng)  # Add up to 20 pts from engagement signal

    # 3. Marketing spend (high = needs ROI/leads)
    spend = company.marketing_spend or 0
    if spend > 100000:
        score += 15
    elif spend > 50000:
        score += 10
    elif spend > 10000:
        score += 5

    # 4. Purchasing frequency (high = buying behavior)
    freq = (company.purchasing_frequency or "").lower()
    if 'high' in freq:
        score += 15
    elif 'medium' in freq or 'average' in freq:
        score += 10
    else:
        score += 5

    # 5. Company size (50-500 ideal)
    size = str(company.company_size or "").replace(',', '')
    if '50-500' in size or size in ['50-200', '201-500'] or (size.isdigit() and 50 <= int(size) <= 500):
        score += 10
    elif '500+' in size or size in ['501-1000', '1000+'] or (size.isdigit() and int(size) > 500):
        score += 5
    else:
        score += 5

    # 6. Revenue (higher = better fit)
    rev = company.revenue or 0
    if rev > 10000000:
        score += 10
    elif rev > 1000000:
        score += 5

    # 7. Payment behavior (good = high quality lead)
    pay = (company.payment_behavior or "").lower()
    if 'good' in pay or 'excellent' in pay or 'prompt' in pay:
        score += 10
    elif 'average' in pay or 'fair' in pay:
        score += 5

    return min(100.0, score)

def process_lead_intent(db: Session, lead_id: int):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
        
    employee = db.query(Employee).filter(Employee.employee_id == lead.employee_id).first()
    company = db.query(Company).filter(Company.company_id == lead.company_id).first()
    
    if employee and company:
        score = calculate_intent_score(employee, company)
        lead.intent_score = score
        db.commit()
        db.refresh(lead)
        
    return lead
