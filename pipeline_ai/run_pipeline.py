import os
import sys

# Add current dir to import path
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.services.dataset_service import ingest_crm_dataset
from app.agents.intent_agent import process_lead_intent
from app.agents.problem_agent import process_lead_problem
from app.agents.sequence_agent import process_lead_sequence
from app.agents.pitch_agent import process_lead_pitch
from app.services.simulation_service import run_full_simulation
from app.models import Lead

def run():
    print("Init DB...")
    init_db()
    
    # Path to lead_database.csv one directory up
    csv_path = os.path.join(os.path.dirname(__file__), "..", "lead_database.csv")
    csv_path = os.path.abspath(csv_path)
    
    if not os.path.exists(csv_path):
        print(f"Warning: dataset not found at {csv_path}. Exiting.")
        return
        
    print("Ingesting Data...")
    ingest_crm_dataset(csv_path)
    
    db = SessionLocal()
    leads = db.query(Lead).all()
    print(f"Running intelligence agents on {len(leads)} leads...")
    
    print(f"Assigning algorithmic intent, problem scoring, and sequence pathways...")
    # Fast loop: Skip slow Pitch generation (email generative string) so simulation finishes in 3 seconds! 
    for lead in leads:
        process_lead_intent(db, lead.id)
        process_lead_problem(db, lead.id)
        process_lead_sequence(db, lead.id)
        # process_lead_pitch(db, lead.id)  <-- Skipped to avoid 10 minute API freeze
        
    print("Simulating User Outreach Events...")
    run_full_simulation(db)
    
    db.close()
    print("Pipeline Execution Context Generation Finished.")

if __name__ == "__main__":
    run()
