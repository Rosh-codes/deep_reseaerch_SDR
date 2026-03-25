# Niche-Based Pipeline Intelligence Engine

An **Agentic SDR (Sales Development Representative) System** built to demonstrate advanced Pipeline Intelligence. This project leverages natural language processing (NLP) and Retrieval-Augmented Generation (RAG) to instantly query a database of leads, evaluate their intent, pinpoint their core problems, and generate highly targeted outreach pitches using Anthropic's Claude models.

## Features

- **🧠 AI Query Engine (RAG)**: Uses **Claude 3 Haiku** to translate your natural language requests (e.g. "Find me mid-sized SaaS companies") into structured database filters instantly.
- **🎯 Intelligent Lead Scoring**: Algorithmic heuristic analysis to assign Intent Scores (0-100) and Outreach Sequences (Hot/Warm/Cold) based on dataset signals.
- **💡 Problem Detection**: Automatically maps company traits and data signals to core business problems.
- **✉️ Deep Research Pitch Generation**: Uses the powerful **Claude 3.5 Sonnet** model to generate a strictly formatted 5-part cold email pitch (Observation -> Problem -> Solution -> Example -> CTA) for matched leads.
- **🔄 Funnel Simulation**: A probabilistic event simulator that mimics a live outbound campaign (opens, clicks, replies, meetings booked) weighted by Lead Intent.
- **📊 Analytics Dashboard**: A sleek Streamlit interface to trace Live Funnel Metrics, High-Converting Signals, and analyze the Live Lead Pipeline.

## System Architecture

The project consists of 5 modular AI "Agents" feeding off a normalized SQLite database:
1. `Query Agent`: NLP -> Local DB Search
2. `Intent Agent`: Signal -> Score
3. `Problem Agent`: Signal -> Problem Mapping
4. `Sequence Agent`: Score -> Campaign Type
5. `Pitch Agent`: Context -> Claude 3.5 Sonnet -> Cold Email

## Quickstart & Setup

### 1. Prerequisites
Ensure you have Python 3.9+ installed and Git configured. 

### 2. Environment Setup
```bash
# Navigate to the project directory
cd pipeline_ai

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all required dependencies
pip install -r requirements.txt
```

### 3. API Keys
1. Locate the `.env` file in the `pipeline_ai` directory.
2. Open it and replace the placeholder with your actual Anthropic API Key:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03...
   ```

### 4. Running the Pipeline
To initialize the SQLite database, ingest the CRM Data, process the AI Agents, and simulate the event outcomes, run:
```bash
python run_pipeline.py
```
*(Note: Because this script deeply processes matches via the Claude API, it may take 1-2 minutes to execute fully.)*

### 5. Launch the Dashboard
Fire up the Streamlit interface to access the Query Engine and view your Agentic Pipeline Analytics:
```bash
streamlit run dashboard/streamlit_app.py
```
