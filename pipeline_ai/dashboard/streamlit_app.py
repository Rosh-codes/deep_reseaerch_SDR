import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import base64

# Ensure imports work from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import settings
from app.database import SessionLocal
from app.models import Lead, Company, Employee
from app.agents.query_agent import parse_user_query
from app.agents.intent_agent import process_lead_intent
from app.agents.problem_agent import process_lead_problem
from app.agents.sequence_agent import process_lead_sequence
from app.agents.report_agent import (
    generate_company_intelligence, 
    generate_outreach_strategy, 
    generate_email_variants,
    generate_pipeline_report
)

def create_download_link(content: str, filename: str, label: str = "📥 Export Report (.md)"):
    b64 = base64.b64encode(str(content).encode('utf-8')).decode('utf-8')
    md_filename = filename.replace('.pdf', '.md')
    href = f'<a href="data:text/markdown;charset=utf-8;base64,{b64}" download="{md_filename}" style="display:inline-block; padding:8px 16px; background-color:#FF4B4B; color:white; text-decoration:none; border-radius:4px; margin-bottom:10px;">{label}</a>'
    return href

engine = create_engine(settings.DATABASE_URL)
st.set_page_config(page_title="Pipeline Intelligence Platform", layout="wide")

page = st.sidebar.radio("Navigation", ["🔍 Sales Intelligence Platform", "📊 Pipeline Analytics"])

# ═══════════════════════════════════════════════
# PAGE 1: SALES INTELLIGENCE
# ═══════════════════════════════════════════════
if page == "🔍 Sales Intelligence Platform":
    st.title("🧠 AI SDR & Sales Intelligence")
    
    user_query = st.text_input("Describe target segment (e.g., 'Find SaaS companies')")
    
    if st.button("Search Database"):
        if not user_query:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Translating query via Claude Haiku..."):
                filters = parse_user_query(user_query)
                st.info(f"Extracted Requirements: {filters}")
                
            db = SessionLocal()
            query = db.query(Lead, Company, Employee).join(Company, Lead.company_id == Company.company_id).join(Employee, Lead.employee_id == Employee.employee_id)
            
            if 'keyword' in filters:
                kw = filters['keyword']
                from sqlalchemy import or_
                query = query.filter(or_(
                    Company.industry.ilike(f"%{kw}%"),
                    Company.company_name.ilike(f"%{kw}%"),
                    Company.description.ilike(f"%{kw}%"),
                    Company.why_needs_help.ilike(f"%{kw}%"),
                    Employee.job_title.ilike(f"%{kw}%"),
                    Lead.problem.ilike(f"%{kw}%")
                ))
            if 'industry' in filters:
                query = query.filter(Company.industry.ilike(f"%{filters['industry']}%"))
            if 'company_size' in filters:
                query = query.filter(Company.company_size.ilike(f"%{filters['company_size']}%"))
            if 'job_title' in filters:
                query = query.filter(Employee.job_title.ilike(f"%{filters['job_title']}%"))
                
            matched_leads = query.all()
            db.close()
            st.success(f"Discovered {len(matched_leads)} matching targets.")
            
            st.session_state['matched_leads'] = matched_leads

    if 'matched_leads' in st.session_state and len(st.session_state['matched_leads']) > 0:
        matched_leads = st.session_state['matched_leads']
        
        st.markdown("### Deep Intelligence Research")
        lead_options = {f"{e.name} ({e.job_title}) @ {c.company_name or 'Company '+str(c.company_id)} ({c.industry})": (l, c, e) for l, c, e in matched_leads}
        selected_key = st.selectbox("Select a Lead to Analyze:", list(lead_options.keys()))
        selected_lead, selected_company, selected_emp = lead_options[selected_key]
        
        if st.button("🚀 Generate Deep Profile & Outreach Strategy"):
            db = SessionLocal()
            process_lead_intent(db, selected_lead.id)
            process_lead_problem(db, selected_lead.id)
            process_lead_sequence(db, selected_lead.id)
            db.close()
            
            # ── CHAIN WORKFLOW PROGRESS ──
            progress = st.progress(0)
            status = st.empty()
            
            status.text("🔗 Step 1/3: Loading verified dataset intelligence...")
            progress.progress(20)
            
            tabs = st.tabs(["🏢 Company Intelligence Report", "🎯 Outreach Strategy", "✉️ Personalized Emails"])
            
            with tabs[0]:
                st.subheader("Company Intelligence Report")
                status.text("🔗 Step 2/3: Scraping live company website...")
                progress.progress(50)
                status.text("🔗 Step 3/3: Claude AI reasoning & analysis...")
                progress.progress(80)
                
                co_intel = generate_company_intelligence(selected_company)
                progress.progress(100)
                status.text("✅ Chain workflow complete!")
                
                st.markdown(create_download_link(co_intel, f"CompanyReport_{selected_company.company_id}.pdf"), unsafe_allow_html=True)
                st.markdown(co_intel, unsafe_allow_html=True)
                
                # Save to session for analytics
                st.session_state['last_report'] = co_intel
                st.session_state['last_company'] = selected_company
                
            with tabs[1]:
                st.subheader("Outreach Strategy")
                with st.spinner("Strategizing optimal outreach approach..."):
                    strategy = generate_outreach_strategy(selected_lead, selected_company, selected_emp)
                st.markdown(create_download_link(strategy, f"Strategy_{selected_emp.name}.pdf"), unsafe_allow_html=True)
                st.markdown(strategy)
                
            with tabs[2]:
                st.subheader("Personalized Email Generator")
                with st.spinner("Generating distinct email variations A/B/C..."):
                    variants = generate_email_variants(selected_lead, selected_company, selected_emp)
                    
                if "error" in variants:
                    st.error(variants["error"])
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info("**Version A: Problem-focused**")
                        st.write(variants.get("email_a_problem", "N/A"))
                    with col2:
                        st.info("**Version B: ROI-focused**")
                        st.write(variants.get("email_b_roi", "N/A"))
                    with col3:
                        st.info("**Version C: Case-study focused**")
                        st.write(variants.get("email_c_case_study", "N/A"))
                        
                    st.success("**AI Recommendation:** " + variants.get("recommendation", ""))

# ═══════════════════════════════════════════════
# PAGE 2: PIPELINE ANALYTICS
# ═══════════════════════════════════════════════
elif page == "📊 Pipeline Analytics":
    st.title("📊 Pipeline Analytics & Charts")
    
    try:
        df_leads = pd.read_sql("SELECT * FROM leads", engine)
        df_events = pd.read_sql("SELECT * FROM events", engine)
        df_companies = pd.read_sql("SELECT * FROM companies", engine)
        df_employees = pd.read_sql("SELECT * FROM employees", engine)
    except Exception as e:
        st.error(f"Database not ready. Run `python run_pipeline.py` first. Error: {e}")
        st.stop()

    # ── KPI METRICS ──
    st.header("📈 KPI Metrics")
    total_leads = len(df_leads)
    
    if not df_events.empty:
        contacted = len(df_events[df_events['event_type'] == 'contacted']['lead_id'].unique())
        opened = len(df_events[df_events['event_type'] == 'opened']['lead_id'].unique())
        replied = len(df_events[df_events['event_type'] == 'replied']['lead_id'].unique())
        positive_replies = len(df_events[df_events['event_type'] == 'positive_reply']['lead_id'].unique())
        booked = len(df_events[df_events['event_type'] == 'meeting_booked']['lead_id'].unique())
        attended = len(df_events[df_events['event_type'] == 'meeting_attended']['lead_id'].unique())
        
        reply_rate = round((replied/contacted)*100, 1) if contacted else 0
        pos_reply_rate = round((positive_replies/replied)*100, 1) if replied else 0
        book_rate = round((booked/contacted)*100, 1) if contacted else 0
        show_rate = round((attended/booked)*100, 1) if booked else 0
    else:
        contacted = opened = replied = positive_replies = booked = attended = 0
        reply_rate = pos_reply_rate = book_rate = show_rate = 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reply Rate", f"{reply_rate}%")
    c2.metric("Positive Reply Rate", f"{pos_reply_rate}%")
    c3.metric("Meeting Booking Rate", f"{book_rate}%")
    c4.metric("Meeting Show-up Rate", f"{show_rate}%")
    
    st.divider()

    # ── DATABASE OVERVIEW ANALYTICS ──
    st.header("🏢 Database Overview")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Industry Distribution
        ind_counts = df_companies['industry'].value_counts().reset_index()
        ind_counts.columns = ['Industry', 'Count']
        fig_ind = px.bar(ind_counts, x='Industry', y='Count', title='Companies by Industry',
                        color='Count', color_continuous_scale='Viridis')
        fig_ind.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig_ind, use_container_width=True)
    
    with col_b:
        # Company Size Distribution
        size_counts = df_companies['company_size'].value_counts().reset_index()
        size_counts.columns = ['Size', 'Count']
        fig_size = px.pie(size_counts, values='Count', names='Size', title='Companies by Size',
                         hole=0.4)
        fig_size.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig_size, use_container_width=True)
    
    col_c, col_d = st.columns(2)
    
    with col_c:
        # Intent Score Distribution
        if 'intent_score' in df_leads.columns:
            fig_intent = px.histogram(df_leads, x='intent_score', nbins=20, 
                                     title='Intent Score Distribution',
                                     color_discrete_sequence=['#FF4B4B'])
            fig_intent.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig_intent, use_container_width=True)
    
    with col_d:
        # Sequence Assignment
        if 'sequence' in df_leads.columns:
            seq_counts = df_leads['sequence'].value_counts().reset_index()
            seq_counts.columns = ['Sequence', 'Count']
            fig_seq = px.bar(seq_counts, x='Sequence', y='Count', title='Lead Sequence Assignment',
                           color='Sequence', color_discrete_map={'Hot':'#FF4B4B', 'Warm':'#FFA500', 'Cold':'#4B9DFF', 'Ignore':'#808080'})
            fig_seq.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig_seq, use_container_width=True)

    st.divider()
    
    # ── SCATTER PLOT: Intent vs Revenue by Industry ──
    st.header("🧠 Intelligence Scatter Analysis")
    
    merged = pd.merge(df_leads, df_companies, on='company_id', how='left')
    merged = pd.merge(merged, df_employees, on='employee_id', how='left')
    
    if 'intent_score' in merged.columns and 'revenue' in merged.columns:
        fig_scatter = px.scatter(merged, x='intent_score', y='revenue', 
                               color='industry', size='intent_score',
                               hover_data=['company_name', 'job_title'],
                               title='Intent Score vs Revenue (by Industry)',
                               labels={'intent_score': 'AI Intent Score', 'revenue': 'Est. Revenue'})
        fig_scatter.update_layout(template='plotly_dark', height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ── FUNNEL CHART ──
    if contacted > 0:
        st.header("🔄 Sales Funnel Conversion")
        
        funnel_data = dict(
            number=[total_leads, contacted, opened, replied, booked, attended],
            stage=["Leads", "Contacted", "Opened", "Replied", "Booked", "Attended"]
        )
        fig_funnel = px.funnel(funnel_data, x='number', y='stage', title='Full Pipeline Funnel')
        fig_funnel.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # ── Best Performers ──
        evt_lead = pd.merge(df_events, df_leads, left_on='lead_id', right_on='id', suffixes=('_ev', '_ld'))
        evt_co = pd.merge(evt_lead, df_companies, on='company_id')
        full_df = pd.merge(evt_co, df_employees, on='employee_id')
        
        best_industry = full_df[full_df['event_type']=='meeting_booked']['industry'].mode()
        best_role = full_df[full_df['event_type']=='meeting_booked']['job_title'].mode()
        best_seq = full_df[full_df['event_type']=='meeting_booked']['sequence'].mode()
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Best Industry", best_industry[0] if not best_industry.empty else "N/A")
        k2.metric("Best Role", best_role[0] if not best_role.empty else "N/A")
        k3.metric("Best Sequence", best_seq[0] if not best_seq.empty else "N/A")
    
    st.divider()
    
    # ── AI EXECUTIVE REPORT ──
    st.header("📋 AI Executive Pipeline Report")
    if st.button("Generate AI Pipeline Report"):
        with st.spinner("Analyzing pipeline data..."):
            payload = {
                "Total Leads": total_leads, "Contacted": contacted, "Booked": booked,
                "Reply Rate": f"{reply_rate}%", "Booking Rate": f"{book_rate}%",
            }
            report = generate_pipeline_report(payload)
            st.markdown(create_download_link(report, "Pipeline_Report.pdf"), unsafe_allow_html=True)
            st.markdown(report)
