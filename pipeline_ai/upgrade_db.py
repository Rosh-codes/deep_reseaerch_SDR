import sqlite3
import pandas as pd
import os

def upgrade_db_with_names():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "lead_database.csv")
    db_path = os.path.join(base_dir, "data", "pipeline.db")
    
    print("Reading CSV...")
    df = pd.read_csv(csv_path)
    
    print("Connecting to SQLite...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE companies ADD COLUMN company_name TEXT")
        print("Added company_name column to DB.")
    except Exception as e:
        print("Column may already exist:", e)
        
    updated = 0
    for idx, row in df.iterrows():
        c_id = idx + 1
        name = str(row.get("Company Name", "Unknown"))
        c.execute("UPDATE companies SET company_name = ? WHERE company_id = ?", (name, c_id))
        updated += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully injected real company names for {updated} organizations!")

if __name__ == "__main__":
    upgrade_db_with_names()
