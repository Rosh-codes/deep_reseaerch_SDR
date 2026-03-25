import pandas as pd
from app.database import SessionLocal, init_db
from app.models import Company, Employee, Lead
import math

def ingest_crm_dataset(csv_path: str):
    init_db()
    db = SessionLocal()
    
    try:
        df = pd.read_csv(csv_path)
        
        for idx, row in df.iterrows():
            if pd.isna(row.get('Company Name')):
                continue
                
            c_id = idx + 1
            
            comp = db.query(Company).filter(Company.company_id == c_id).first()
            if not comp:
                comp = Company(
                    company_id=c_id,
                    industry=str(row.get('Industry / Category', str(row.get('Category', '')))),
                    company_size=str(row.get('Estimated Company Size', '')),
                    revenue=1000000.0, # Mock 
                    marketing_spend=50000.0, # Mock
                    purchasing_frequency='Medium',
                    payment_behavior='Good'
                )
                db.add(comp)
                
            emp = db.query(Employee).filter(Employee.employee_id == c_id).first()
            if not emp:
                job_title = str(row.get('Target Role for Outreach', ''))
                email = str(row.get('Mock contact email', ''))
                
                emp = Employee(
                    employee_id=c_id,
                    company_id=c_id,
                    name=email.split('@')[0].capitalize() if '@' in email else "Unknown",
                    job_title=job_title,
                    seniority=job_title,
                    tenure=2.0,
                    engagement_score=70.0,
                    contact_preference='Email'
                )
                db.add(emp)
                
            lead = db.query(Lead).filter(Lead.employee_id == c_id).first()
            if not lead:
                lead = Lead(
                    employee_id=c_id,
                    company_id=c_id,
                    status="new",
                    problem=str(row.get('Why this company might need more leads / sales / automation', ''))
                )
                db.add(lead)
            
        db.commit()
        count = db.query(Lead).count()
        print(f"[DatasetService] Ingested flat CSV. Total leads: {count}")
    
    except Exception as e:
        db.rollback()
        print(f"[DatasetService] Error ingesting dataset: {e}")
    finally:
        db.close()
