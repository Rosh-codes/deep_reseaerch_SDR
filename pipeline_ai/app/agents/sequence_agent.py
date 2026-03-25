from sqlalchemy.orm import Session
from app.models import Lead

def map_intent_to_sequence(score: float) -> str:
    """
    Score bounds:
    80-100: Hot
    60-79: Warm
    40-59: Cold
    <40: Ignore
    """
    if score >= 80:
        return "Hot"
    elif score >= 60:
        return "Warm"
    elif score >= 40:
        return "Cold"
    else:
        return "Ignore"

def process_lead_sequence(db: Session, lead_id: int):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
        
    score = lead.intent_score or 0.0
    lead.sequence = map_intent_to_sequence(score)
    db.commit()
    db.refresh(lead)
    
    return lead
