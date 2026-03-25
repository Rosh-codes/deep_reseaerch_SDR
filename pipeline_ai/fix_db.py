import pandas as pd
from app.database import SessionLocal
from app.models import Company
import os
import sys

sys.path.append(os.path.dirname(__file__))

def patch_database():
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lead_database.csv"))
    if not os.path.exists(csv_path):
        print(f"CSV not found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    db = SessionLocal()
    
    updates = 0
    for idx, row in df.iterrows():
        c_id = idx + 1
        comp = db.query(Company).filter(Company.company_id == c_id).first()
        if comp:
            cat = str(row.get('Category', ''))
            sub = str(row.get('Industry / Category', ''))
            # Combine both parent category and sub industry so wildcard searches match perfectly
            comp.industry = f"{cat} - {sub}"
            updates += 1
            
    db.commit()
    db.close()
    print(f"Database patched successfully with updated Industry structures for {updates} rows.")

if __name__ == "__main__":
    patch_database()
