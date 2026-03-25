from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional
from pydantic import BaseModel
import uvicorn

from app.database import get_db, init_db
from app.models import Company, Employee, Lead, Event, Action


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Pipeline Intelligence Engine API",
    description="Agentic SDR system API managing intent, pitches, and sequencing.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Shared serialisers ───────────────────────────────────────────────────────

def _company_dict(comp: Company) -> dict:
    return {
        "name": comp.company_name,
        "industry": comp.industry,
        "size": comp.company_size,
        "country": comp.country,
        "website_url": comp.website_url,
        "description": comp.description,
        "why_needs_help": comp.why_needs_help,
        "outreach_angle": comp.outreach_angle,
        "revenue": comp.revenue,
        "marketing_spend": comp.marketing_spend,
        "purchasing_frequency": comp.purchasing_frequency,
        "payment_behavior": comp.payment_behavior,
    }


def _employee_dict(emp: Employee) -> dict:
    return {
        "name": emp.name,
        "job_title": emp.job_title,
        "seniority": emp.seniority,
        "tenure": emp.tenure,
        "engagement_score": emp.engagement_score,
        "contact_preference": emp.contact_preference,
    }


def _lead_row(lead: Lead, emp: Employee, comp: Company) -> dict:
    return {
        "id": lead.id,
        "intent_score": lead.intent_score,
        "problem": lead.problem,
        "sequence": lead.sequence,
        "status": lead.status,
        "employee": _employee_dict(emp),
        "company": _company_dict(comp),
    }


# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pipeline Intelligence Engine v2"}


# ─── LEADS ────────────────────────────────────────────────────────────────────

@app.get("/api/leads")
def list_leads(
    db: Session = Depends(get_db),
    sequence: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = Query(200, le=1000),
    offset: int = 0,
):
    q = (
        db.query(Lead, Employee, Company)
        .join(Employee, Lead.employee_id == Employee.employee_id)
        .join(Company, Lead.company_id == Company.company_id)
    )
    if sequence:
        q = q.filter(Lead.sequence == sequence)
    if industry:
        q = q.filter(Company.industry.ilike(f"%{industry}%"))

    return [_lead_row(lead, emp, comp) for lead, emp, comp in q.offset(offset).limit(limit)]


class SearchRequest(BaseModel):
    query: str


@app.post("/api/leads/search")
def search_leads(req: SearchRequest, db: Session = Depends(get_db)):
    from app.agents.query_agent import parse_user_query

    filters = parse_user_query(req.query)
    q = (
        db.query(Lead, Employee, Company)
        .join(Employee, Lead.employee_id == Employee.employee_id)
        .join(Company, Lead.company_id == Company.company_id)
    )
    if filters.get("industry"):
        q = q.filter(Company.industry.ilike(f"%{filters['industry']}%"))
    if filters.get("company_size"):
        q = q.filter(Company.company_size.ilike(f"%{filters['company_size']}%"))
    if filters.get("job_title"):
        q = q.filter(Employee.job_title.ilike(f"%{filters['job_title']}%"))
    if filters.get("keyword"):
        kw = f"%{filters['keyword']}%"
        q = q.filter(or_(
            Company.why_needs_help.ilike(kw),
            Company.description.ilike(kw),
            Company.outreach_angle.ilike(kw),
            Company.industry.ilike(kw),
        ))

    results = q.limit(100).all()
    return {
        "filters_applied": filters,
        "results": [_lead_row(lead, emp, comp) for lead, emp, comp in results],
    }


@app.get("/api/leads/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Lead, Employee, Company)
        .join(Employee, Lead.employee_id == Employee.employee_id)
        .join(Company, Lead.company_id == Company.company_id)
        .filter(Lead.id == lead_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead, emp, comp = result
    events = db.query(Event).filter(Event.lead_id == lead_id).order_by(Event.timestamp).all()
    actions = db.query(Action).filter(Action.lead_id == lead_id).order_by(Action.timestamp).all()

    row = _lead_row(lead, emp, comp)
    row["pitch"] = lead.pitch
    row["events"] = [{"type": e.event_type, "timestamp": e.timestamp.isoformat()} for e in events]
    row["actions"] = [{"action": a.recommended_action, "status": a.status, "timestamp": a.timestamp.isoformat()} for a in actions]
    return row


@app.get("/api/leads/{lead_id}/intelligence")
def get_intelligence(lead_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Lead, Employee, Company)
        .join(Employee, Lead.employee_id == Employee.employee_id)
        .join(Company, Lead.company_id == Company.company_id)
        .filter(Lead.id == lead_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    _, _, comp = result
    from app.agents.report_agent import generate_company_intelligence
    return {"report": generate_company_intelligence(comp)}


@app.get("/api/leads/{lead_id}/strategy")
def get_strategy(lead_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Lead, Employee, Company)
        .join(Employee, Lead.employee_id == Employee.employee_id)
        .join(Company, Lead.company_id == Company.company_id)
        .filter(Lead.id == lead_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead, emp, comp = result
    from app.agents.report_agent import generate_outreach_strategy
    return {"strategy": generate_outreach_strategy(lead, comp, emp)}


@app.get("/api/leads/{lead_id}/emails")
def get_email_variants(lead_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Lead, Employee, Company)
        .join(Employee, Lead.employee_id == Employee.employee_id)
        .join(Company, Lead.company_id == Company.company_id)
        .filter(Lead.id == lead_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead, emp, comp = result
    from app.agents.report_agent import generate_email_variants
    return generate_email_variants(lead, comp, emp)


# ─── ANALYTICS ────────────────────────────────────────────────────────────────

@app.get("/api/leads/meta")
def get_leads_meta(db: Session = Depends(get_db)):
    """Returns distinct searchable values from the demo dataset."""
    industries = sorted(set(
        r[0] for r in db.query(Company.industry.distinct()).all() if r[0]
    ))
    titles = sorted(set(
        r[0] for r in db.query(Employee.job_title.distinct()).all() if r[0]
    ))
    countries = sorted(set(
        r[0] for r in db.query(Company.country.distinct()).all()
        if r[0] and r[0] != 'nan'
    ))
    # Derive broad keyword buckets from industry names
    buckets = {
        "AI": [i for i in industries if 'AI' in i or 'ai' in i.lower()],
        "SaaS": [i for i in industries if 'SaaS' in i or 'saas' in i.lower()],
        "Recruitment": [i for i in industries if 'recruit' in i.lower() or 'staffing' in i.lower() or 'talent' in i.lower()],
        "Marketing": [i for i in industries if 'marketing' in i.lower() or 'demand gen' in i.lower()],
        "Fintech": [i for i in industries if 'bank' in i.lower() or 'payment' in i.lower() or 'financ' in i.lower() or 'fintech' in i.lower()],
        "Consulting": [i for i in industries if 'consult' in i.lower() or 'IT services' in i.lower()],
        "DTC": [i for i in industries if 'DTC' in i or 'brand' in i.lower() or 'apparel' in i.lower()],
    }
    keyword_groups = {k: v for k, v in buckets.items() if v}
    return {
        "industries": industries,
        "job_titles": titles,
        "countries": countries,
        "keyword_groups": keyword_groups,
        "sample_searches": [
            "AI companies that need automation",
            "SaaS companies with head of sales",
            "recruitment agencies needing outbound",
            "fintech companies needing sales leads",
            "DTC brands needing marketing",
            "consulting firms needing demand gen",
        ],
    }


@app.get("/api/analytics/funnel")
def get_funnel(db: Session = Depends(get_db)):
    total = db.query(func.count(Lead.id)).scalar()
    event_types = ["contacted", "opened", "clicked", "replied", "positive_reply", "meeting_booked", "meeting_attended"]
    funnel = {"total_leads": total}
    for et in event_types:
        funnel[et] = db.query(func.count(Event.lead_id.distinct())).filter(Event.event_type == et).scalar()
    return funnel


@app.get("/api/analytics/performance")
def get_performance(db: Session = Depends(get_db)):
    # By sequence
    by_sequence = {}
    for seq in ["Hot", "Warm", "Cold", "Ignore"]:
        lead_ids = [r[0] for r in db.query(Lead.id).filter(Lead.sequence == seq).all()]
        if not lead_ids:
            continue
        total = len(lead_ids)
        replied = db.query(func.count(Event.id.distinct())).filter(Event.lead_id.in_(lead_ids), Event.event_type == "replied").scalar()
        booked = db.query(func.count(Event.id.distinct())).filter(Event.lead_id.in_(lead_ids), Event.event_type == "meeting_booked").scalar()
        by_sequence[seq] = {
            "total": total,
            "replied": replied,
            "meeting_booked": booked,
            "reply_rate": round(replied / total * 100, 1) if total else 0,
            "booking_rate": round(booked / total * 100, 1) if total else 0,
        }

    # By industry
    industries = [r[0] for r in db.query(Company.industry.distinct()).all() if r[0]]
    by_industry = {}
    for ind in industries:
        lead_ids = [
            r[0] for r in db.query(Lead.id)
            .join(Company, Lead.company_id == Company.company_id)
            .filter(Company.industry == ind).all()
        ]
        total = len(lead_ids)
        if not total:
            continue
        replied = db.query(func.count(Event.id.distinct())).filter(Event.lead_id.in_(lead_ids), Event.event_type == "replied").scalar()
        by_industry[ind] = {"total": total, "replied": replied, "reply_rate": round(replied / total * 100, 1)}

    # By country
    countries = [r[0] for r in db.query(Company.country.distinct()).all() if r[0] and r[0] != 'nan']
    by_country = {}
    for country in countries:
        lead_ids = [
            r[0] for r in db.query(Lead.id)
            .join(Company, Lead.company_id == Company.company_id)
            .filter(Company.country == country).all()
        ]
        total = len(lead_ids)
        if total:
            by_country[country] = {"total": total}

    # KPIs
    total = db.query(func.count(Lead.id)).scalar()
    contacted = db.query(func.count(Event.lead_id.distinct())).filter(Event.event_type == "contacted").scalar()
    replied = db.query(func.count(Event.lead_id.distinct())).filter(Event.event_type == "replied").scalar()
    booked = db.query(func.count(Event.lead_id.distinct())).filter(Event.event_type == "meeting_booked").scalar()
    attended = db.query(func.count(Event.lead_id.distinct())).filter(Event.event_type == "meeting_attended").scalar()

    return {
        "kpis": {
            "total_leads": total,
            "contacted": contacted,
            "reply_rate": round(replied / contacted * 100, 1) if contacted else 0,
            "booking_rate": round(booked / contacted * 100, 1) if contacted else 0,
            "show_up_rate": round(attended / booked * 100, 1) if booked else 0,
        },
        "by_sequence": by_sequence,
        "by_industry": by_industry,
        "by_country": by_country,
    }


@app.get("/api/analytics/report")
def get_analytics_report(db: Session = Depends(get_db)):
    total = db.query(func.count(Lead.id)).scalar()
    funnel = {}
    for et in ["contacted", "opened", "replied", "meeting_booked", "meeting_attended"]:
        funnel[et] = db.query(func.count(Event.lead_id.distinct())).filter(Event.event_type == et).scalar()

    seq_perf = {}
    for seq in ["Hot", "Warm", "Cold"]:
        lead_ids = [r[0] for r in db.query(Lead.id).filter(Lead.sequence == seq).all()]
        total_seq = len(lead_ids)
        if total_seq:
            booked = db.query(func.count(Event.id.distinct())).filter(Event.lead_id.in_(lead_ids), Event.event_type == "meeting_booked").scalar()
            seq_perf[seq] = {"total": total_seq, "meeting_booked": booked, "booking_rate": f"{round(booked / total_seq * 100, 1)}%"}

    metrics = {"total_leads": total, "funnel": funnel, "sequence_performance": seq_perf}
    from app.agents.report_agent import generate_pipeline_report
    return {"report": generate_pipeline_report(metrics), "metrics": metrics}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
