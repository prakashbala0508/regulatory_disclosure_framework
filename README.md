# Regulatory Disclosure Review Framework

Analyzes 320 simulated employee disclosure records modeled on FINRA BrokerCheck
categories, with severity classification, escalation logic, and SLA tracking.

## Features
- 320 simulated BrokerCheck disclosure records across 15 categories
- Severity triage engine: CRITICAL / HIGH / MEDIUM / LOW
- FINRA Rule 4530 30-day filing timeliness tracker
- Visual + text decision tree for disclosure review workflow
- 8-tab Excel audit report with review checklist
- Plain-English regulatory reference guide (Rules 4530, 17a-3, 3270, 17a-4)
- Record lookup by name, Employee ID, or Record ID

## Tech Stack
Python, Streamlit, Pandas, Plotly, OpenPyXL, Matplotlib, Faker

## Run Locally
pip install -r requirements.txt
streamlit run app.py