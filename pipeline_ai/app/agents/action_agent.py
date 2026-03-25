from sqlalchemy.orm import Session
from app.models import Event, Action, Lead

def determine_next_action(event_type: str) -> str:
    mapping = {
        "contacted": "Wait",
        "opened": "Send follow-up",
        "clicked": "Send case study",
        "replied": "Continue conversation",
        "positive_reply": "Send booking link",
        "negative_reply": "Stop outreach",
        "meeting_booked": "Trigger reminders",
        "meeting_attended": "Send post-meeting materials"
    }
    return mapping.get(event_type, "Pause sequence")

def process_new_event(db: Session, event_id: int):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None
        
    lead = db.query(Lead).filter(Lead.id == event.lead_id).first()
    if not lead:
        return None
        
    recommended_action = determine_next_action(event.event_type)
    
    action = Action(
        lead_id=lead.id,
        recommended_action=recommended_action,
        status="pending"
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    
    return action
