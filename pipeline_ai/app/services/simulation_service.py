import random
from sqlalchemy.orm import Session
from app.models import Lead, Event
from app.agents.action_agent import process_new_event

def simulate_events_for_lead(db: Session, lead: Lead) -> None:
    intent = lead.intent_score or 0.0
    
    # Base probabilities mapped tightly to Intent Score weights
    if intent >= 80:
        p_open, p_reply, p_pos, p_book = 0.8, 0.4, 0.2, 0.15
    elif intent >= 60:
        p_open, p_reply, p_pos, p_book = 0.6, 0.2, 0.1, 0.05
    elif intent >= 40:
        p_open, p_reply, p_pos, p_book = 0.3, 0.05, 0.01, 0.005
    else:
        p_open, p_reply, p_pos, p_book = 0.1, 0.01, 0.0, 0.0

    events_to_create = ["contacted"]
    
    if random.random() < p_open:
        events_to_create.append("opened")
        if random.random() < 0.5: # 50% chance of clicking link if opened
            events_to_create.append("clicked")
            
        if random.random() < p_reply:
            events_to_create.append("replied")
            
            # positive ratio mapping
            pos_ratio = (p_pos / p_reply) if p_reply > 0 else 0
            if random.random() < pos_ratio:
                events_to_create.append("positive_reply")
                
                # book ratio mapping
                book_ratio = (p_book / p_pos) if p_pos > 0 else 0
                if random.random() < book_ratio:
                    events_to_create.append("meeting_booked")
                    
                    if random.random() < 0.8: # high show-up rate
                        events_to_create.append("meeting_attended")
            else:
                events_to_create.append("negative_reply")

    # Insert sequential events and generate actions
    for evt_type in events_to_create:
        evt = Event(lead_id=lead.id, event_type=evt_type)
        db.add(evt)
        db.commit()
        db.refresh(evt)
        # Immediately process next best action logic triggers
        process_new_event(db, evt.id)
        
    lead.status = events_to_create[-1]
    db.commit()


def run_full_simulation(db: Session):
    leads = db.query(Lead).all()
    print(f"Starting pipeline event simulation for {len(leads)} leads...")
    count = 0
    for lead in leads:
        # Check against existing simulations
        limit = db.query(Event).filter(Event.lead_id == lead.id).count()
        if limit == 0:
            simulate_events_for_lead(db, lead)
            count += 1
    print(f"Simulation mapped events for {count} new leads.")
