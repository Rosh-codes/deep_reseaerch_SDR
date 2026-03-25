# Deep Research SDR Agent

> An AI-powered Sales Intelligence Platform built as a multi-agent pipeline on top of **Leadsforge + Salesforge**, designed to automate B2B lead research, qualification, and outreach strategy using Claude Haiku 4.5.

---

## What This Project Does (Current Implementation)

This system takes a raw CSV dataset of 114 B2B companies (simulating Leadsforge lead data) and runs them through a **multi-agent AI pipeline** that:

1. **Ingests lead data** into a local SQLite database with full company profiles (name, industry, size, website, description, pain points)
2. **Scores every lead** with a buying intent score (0–100) using a 7-signal heuristic model
3. **Detects pain points** for each company based on their size, marketing spend, and engagement levels
4. **Assigns outreach sequences** (Hot / Warm / Cold / Ignore) based on intent scores
5. **Generates Company Intelligence Reports** using Claude Haiku — combining dataset intelligence with live website scraping (requests + BeautifulSoup) to produce detailed research on each company
6. **Generates Outreach Strategy Plans** — lead priority, sequence cadence, channel recommendations, and conversion probability estimates
7. **Generates 3 personalized email variants** (Problem-focused / ROI-focused / Case-study focused) using XML-based extraction to avoid JSON parsing errors
8. **Visualizes pipeline analytics** — KPI metrics, industry/size distributions, intent score histograms, scatter plots, and sales funnel conversion charts

---

## How It Works

### Pipeline Initialization (`run_pipeline.py`)
```
CSV Ingestion → Intent Scoring → Problem Detection → Sequence Assignment → Event Simulation
```
- Reads `lead_database.csv` and creates Company, Employee, and Lead records in SQLite
- Runs 3 AI agents (Intent, Problem, Sequence) on all 114 leads
- Simulates outreach events (opens, replies, bookings) for the analytics dashboard

### Streamlit Dashboard (`streamlit_app.py`)

**Page 1 — Sales Intelligence Platform:**
- User types a natural language query (e.g., "find companies that need automation")
- Claude Haiku extracts search keywords and queries the database across 6 columns (industry, company name, description, pain points, job title, lead problem)
- User selects a lead and clicks "Generate Deep Profile"
- System runs a 3-step chain:
  - **Step 1:** Loads verified company data from the database
  - **Step 2:** Scrapes the company's actual website using requests + BeautifulSoup
  - **Step 3:** Feeds everything into Claude Haiku for analysis and report generation
- Generates: Intelligence Report → Outreach Strategy → 3 Email Variants

**Page 2 — Pipeline Analytics:**
- KPI metrics (reply rate, booking rate, show-up rate)
- Industry and company size distribution charts
- Intent score histogram and sequence breakdown
- Intent vs Revenue scatter plot (colored by industry)
- Sales funnel conversion chart
- AI-generated Pipeline Intelligence Report

---

## Setup & Run

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate          # Windows

# Install dependencies
cd pipeline_ai
pip install -r requirements.txt
pip install beautifulsoup4

# Add your API key to .env
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Step 1: Initialize database and run agents
python run_pipeline.py

# Step 2: Launch dashboard
streamlit run dashboard/streamlit_app.py
```

### 3. Start the FastAPI Backend

## Project Structure

```
pipeline/
├── lead_database.csv                # Leadsforge dataset (114 companies)
├── README.md
└── pipeline_ai/
    ├── .env                         # API key configuration
    ├── run_pipeline.py              # Pipeline orchestrator
    ├── data/pipeline.db             # SQLite database
    ├── app/
    │   ├── config.py                # Environment settings
    │   ├── database.py              # SQLAlchemy engine
    │   ├── models.py                # ORM schema
    │   ├── agents/
    │   │   ├── intent_agent.py      # Intent scoring (0-100)
    │   │   ├── problem_agent.py     # Pain point detection
    │   │   ├── sequence_agent.py    # Hot/Warm/Cold/Ignore
    │   │   ├── pitch_agent.py       # Cold email generation
    │   │   ├── query_agent.py       # NL→SQL query parser
    │   │   └── report_agent.py      # Intelligence, Strategy, Email, Analytics agents
    │   └── services/
    │       ├── dataset_service.py   # CSV ingestion
    │       └── simulation_service.py # Event simulation
    └── dashboard/
        └── streamlit_app.py         # Streamlit UI
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Engine | Claude Haiku 4.5 (Anthropic API) |
| Database | SQLite + SQLAlchemy ORM |
| Web Scraping | requests + BeautifulSoup4 |
| Frontend | Streamlit |
| Visualization | Plotly |
| Export | Markdown file download |
