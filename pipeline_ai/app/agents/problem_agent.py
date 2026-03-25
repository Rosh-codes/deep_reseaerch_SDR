from sqlalchemy.orm import Session
from app.models import Lead, Employee, Company

def detect_problem(employee: Employee, company: Company) -> str:
    # High marketing spend
    spend = company.marketing_spend or 0
    if spend > 75000:
        return "Needs better marketing ROI"
        
    # High purchasing frequency
    freq = (company.purchasing_frequency or "").lower()
    if 'high' in freq:
        return "Scaling / Ready to buy"
        
    # Low engagement score
    eng = employee.engagement_score or 0
    if eng < 40: # Assuming 100 is max based on our intent mappings
        return "Needs nurturing"
        
    # Company size logic
    size_str = str(company.company_size or "").lower()
    if 'small' in size_str or size_str in ['1-10', '11-50', 'micro']:
        return "Needs automation"
    elif 'large' in size_str or 'enterprise' in size_str or size_str in ['500+', '1000+']:
        return "Needs efficiency and scaling"
        
    # Default fallback just catching general needs
    return "Needs pipeline optimization"

def process_lead_problem(db: Session, lead_id: int):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
        
    employee = db.query(Employee).filter(Employee.employee_id == lead.employee_id).first()
    company = db.query(Company).filter(Company.company_id == lead.company_id).first()
    
    if employee and company:
        problem = detect_problem(employee, company)
        lead.problem = problem
        db.commit()
        db.refresh(lead)
        
    return lead
