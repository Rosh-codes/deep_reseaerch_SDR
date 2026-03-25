from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.database import Base

class Company(Base):
    __tablename__ = "companies"
    
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    industry = Column(String, index=True)
    company_size = Column(String)
    revenue = Column(Float)
    marketing_spend = Column(Float)
    purchasing_frequency = Column(String)
    payment_behavior = Column(String)
    # Rich dataset fields
    description = Column(Text, nullable=True)
    website_url = Column(String, nullable=True)
    why_needs_help = Column(Text, nullable=True)
    outreach_angle = Column(Text, nullable=True)
    country = Column(String, nullable=True)

class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), index=True)
    name = Column(String)
    job_title = Column(String)
    seniority = Column(String)
    tenure = Column(Float)
    engagement_score = Column(Float)
    contact_preference = Column(String)

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    
    # AI Engine Outputs
    intent_score = Column(Float, default=0.0)
    problem = Column(String, nullable=True)
    sequence = Column(String, nullable=True)  # Hot / Warm / Cold / Ignore
    pitch = Column(Text, nullable=True)
    
    # State tracking
    status = Column(String, default="new") 

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), index=True)
    event_type = Column(String) # opened, clicked, replied, positive_reply, negative_reply, meeting_booked, meeting_attended
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Action(Base):
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), index=True)
    recommended_action = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="pending")
