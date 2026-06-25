# Policy POC

Small Streamlit demo for the Cotiviti intern assessment (Topic 3: Content Management in Health Care).

It walks through three things teams do when billing policy changes:

1. Summarize a long policy doc
2. Compare an old version to a new one
3. Pull PTP/MUE rules into JSON (for review before any production use)

All data here is fake sample text — not real PHI and not from CMS.

## Setup

```bash
cd "Proof of Concept"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL (usually http://localhost:8501).

## Files

- `app.py` — UI
- `engine/` — summarizer, differ, rule extractor
- `data/` — two sample NCCI-style policy versions (Q1 and Q2 2025)

Summarize uses keyword scoring. Compare uses `difflib` plus regex. Rule extract uses regex parsers. No external APIs.
