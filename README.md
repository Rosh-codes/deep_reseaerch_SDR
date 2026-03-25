# Deep Research SDR Agent Pipeline

An autonomous Sales Intelligence platform that ingests raw CRM datasets, research domains via live web-scraping pipelines, and outputs hyper-personalized outreach leveraging Claude 4.5 Haiku.

## Architecture & Capabilities

1. **RAG Database Pipeline**: Ingests flat `.csv` lead files into a highly relational local SQLite map.
2. **AI Intent & Problem Agents**: Algorithmically predicts buying intent scores and pinpoints specific B2B operational bottlenecks dynamically.
3. **Live Web OSINT Search**: Bypasses stagnant dataset limits by natively streaming live DuckDuckGo intelligence (company news, corporate hiring footprints, & high-res corporate media) into the context window.
4. **Deep Sequence Modeling**: Employs Anthropic's lightning-fast `claude-haiku-4-5` to synthesize massive company intelligence profiles directly in the dashboard.
5. **XML Robust Email Engine**: Generates highly specialized Cold, Warm, and Ignore messaging variants. Utilizes custom XML extraction logic to neutralize JSON parse truncation bugs during massive string generation.

---

## Setup Instructions

### Environment Verification
Ensure you have Python 3.10+ installed and create a Virtual Environment:
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate   

# Mac/Linux
source venv/bin/activate
```

### Installation
```bash
cd pipeline_ai
pip install -r requirements.txt
pip install duckduckgo-search
```

### Configuration
1. Open the `.env` file located in the `pipeline_ai` directory.
2. Insert your active Anthropic API Key (`sk-ant-...`).
> **Note**: The agents are globally configured to run strictly on the ultra-cheap, highly performant `claude-haiku-4-5` endpoint to minimize token overhead.

---

## Execution Launch

### 1. Ingest CRM Database
Process your raw lead data into the SQLite engine natively:
```bash
python pipeline_ai/run_pipeline.py
```
*(Tip: Once `Init DB...` finishes processing the leads, you can interrupt exactly here (`Ctrl+C`) to skip the synchronous terminal logging and jump straight into the visual frontend).*

### 2. Launch Streamlit Intelligence Platform
Start your server on `localhost`:
```bash
streamlit run pipeline_ai/dashboard/streamlit_app.py
```

### Platform Features
- **Markdown AI Exports**: Intelligence Reports dynamically stream down as universally readable `.md` strings for fast CRM copy-pasting.
- **Live Search Images**: Streams actual live-scraped corporate logs and software analytics into the platform UI.
- **KPI Funnel Analytics**: Interactive visual abstractions built with `plotly` analyzing the granular conversion rate performance of your cold sequences!
