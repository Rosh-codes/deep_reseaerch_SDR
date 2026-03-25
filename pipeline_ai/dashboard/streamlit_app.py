import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import settings
from app.database import SessionLocal
from app.models import Lead, Company, Employee
from app.agents.query_agent import parse_user_query
from app.agents.intent_agent import process_lead_intent
from app.agents.problem_agent import process_lead_problem
from app.agents.sequence_agent import process_lead_sequence
from app.agents.pitch_agent import process_lead_pitch

engine = create_engine(settings.DATABASE_URL)

st.set_page_config(page_title="Pipeline Intelligence Engine", layout="wide")

page = st.sidebar.radio("Navigation", ["🔍 AI Query Engine", "📊 Analytics Funnel"])

if page == "🔍 AI Query Engine":
    st.title("🧠 Natural Language Lead Search")
    st.markdown("Ask natural language questions. We use **Claude Haiku (Retrieval/Routing)** to translate the query into local DB filters, and **Claude Sonnet 3.5 (Deep Research)** to generate customized pitches.")
    
    user_query = st.text_input("Search (e.g., 'Find B2B SaaS companies' or 'Looking for Fintech leads in Medium size')")
    
    if st.button("Search Database & Run Pipeline"):
        if not user_query:
            st.warning("Please enter a query to match leads.")
        else:
            with st.spinner("Translating query to dataset filters using Claude Haiku..."):
                filters = parse_user_query(user_query)
                st.info(f"Extracted Requirements: {filters}")
                
            with st.spinner("Searching Local Database..."):
                db = SessionLocal()
                query = db.query(Lead, Company, Employee).join(Company, Lead.company_id == Company.company_id).join(Employee, Lead.employee_id == Employee.employee_id)
                
                if 'industry' in filters:
                    query = query.filter(Company.industry.ilike(f"%{filters['industry']}%"))
                if 'company_size' in filters:
                    query = query.filter(Company.company_size.ilike(f"%{filters['company_size']}%"))
                if 'job_title' in filters:
                    query = query.filter(Employee.job_title.ilike(f"%{filters['job_title']}%"))
                    
                matched_leads = query.all()
                db.close()
                st.success(f"Discovered {len(matched_leads)} matching targets in the knowledge base!")
                
            if len(matched_leads) > 0:
                st.markdown("### 🤖 Deep Pipeline Generation")
                st.caption("Running Intensive Outreach Generation leveraging Claude Sonnet (limited to top 3 for speed).")
                
                db = SessionLocal()
                for idx, (l, c, e) in enumerate(matched_leads[:3]): # Processing top 3 specifically
                    st.write("---")
                    st.markdown(f"**Target:** {e.name} | {e.job_title} @ {c.industry} Firm")
                    
                    process_lead_intent(db, l.id)
                    process_lead_problem(db, l.id)
                    process_lead_sequence(db, l.id)
                    
                    with st.spinner(f"Sonnet 3.5 researching and generating pitch for {e.name}..."):
                        updated_lead = process_lead_pitch(db, l.id)
                        
                    st.markdown(f"**Assigned Sequence:** `{updated_lead.sequence}` | **Intent Score:** `{updated_lead.intent_score}`")
                    st.markdown(f"**Detected Problem:** {updated_lead.problem}")
                    st.info(updated_lead.pitch)
                db.close()
                st.balloons()
            else:
                st.error("No leads matched your criteria.")

elif page == "📊 Analytics Funnel":
    st.title("🎯 Pipeline Analytics Engine")
    try:
        df_leads = pd.read_sql("SELECT * FROM leads", engine)
        df_events = pd.read_sql("SELECT * FROM events", engine)
        df_companies = pd.read_sql("SELECT * FROM companies", engine)
        df_employees = pd.read_sql("SELECT * FROM employees", engine)
    except Exception as e:
        st.error(f"Waiting for database generation. Error: {e}")
        st.stop()

    st.header("Conversion Funnel")
    total_leads = len(df_leads)
    if not df_events.empty:
        contacted = len(df_events[df_events['event_type'] == 'contacted']['lead_id'].unique())
        opened = len(df_events[df_events['event_type'] == 'opened']['lead_id'].unique())
        replied = len(df_events[df_events['event_type'] == 'replied']['lead_id'].unique())
        positive_replies = len(df_events[df_events['event_type'] == 'positive_reply']['lead_id'].unique())
        meetings_booked = len(df_events[df_events['event_type'] == 'meeting_booked']['lead_id'].unique())
        meetings_attended = len(df_events[df_events['event_type'] == 'meeting_attended']['lead_id'].unique())
    else:
        contacted = opened = replied = positive_replies = meetings_booked = meetings_attended = 0

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("Leads", total_leads)
    c2.metric("Contacted", contacted)
    c3.metric("Opened", opened)
    c4.metric("Replied", replied)
    c5.metric("Positive", positive_replies)
    c6.metric("Booked", meetings_booked)
    c7.metric("Attended", meetings_attended)

    st.divider()
    st.header("Pipeline Insights")
    if not df_events.empty and not df_leads.empty:
        booked_lead_ids = df_events[df_events['event_type'] == 'meeting_booked']['lead_id'].unique()
        booked_leads = df_leads[df_leads['id'].isin(booked_lead_ids)]
        if len(booked_leads) > 0:
            booked_full = booked_leads.merge(df_companies, on='company_id', how='left').merge(df_employees, on='employee_id', how='left')
            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                st.subheader("Best Industry")
                st.info(booked_full['industry'].mode()[0] if not booked_full['industry'].empty else "N/A")
                st.subheader("Best Job Title")
                st.info(booked_full['job_title'].mode()[0] if not booked_full['job_title'].empty else "N/A")
            with col_ins2:
                st.subheader("Best Size")
                st.info(booked_full['company_size'].mode()[0] if not booked_full['company_size'].empty else "N/A")
                st.subheader("Best Sequence")
                st.info(booked_full['sequence'].mode()[0] if not booked_full['sequence'].empty else "N/A")
            
            st.subheader("High-Converting AI Signals")
            fig_data = booked_full['problem'].value_counts().reset_index()
            fig_data.columns = ['Detected Problem', 'Meetings Booked']
            st.dataframe(fig_data, use_container_width=True)
        else:
            st.warning("No meetings booked yet.")
    st.divider()
    st.header("Live Lead Flow Preview")
    if not df_leads.empty:
        st.dataframe(df_leads[['id', 'intent_score', 'problem', 'sequence', 'status', 'pitch']].head(15), use_container_width=True)
