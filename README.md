# Vital8 Heart Health Score

Vital8 is a Streamlit prototype for a free, educational cardiovascular health score based on the American Heart Association's Life's Essential 8 framework.

The app asks for eight prevention domains, returns a 0-100 score, highlights the highest-yield opportunities, and offers optional exploratory layers for cardiorespiratory fitness, hsCRP, and Lp(a). It is designed for patient-facing education, not diagnosis or treatment.

## What It Does

- Calculates an LE8-style score from available lifestyle, lab, body-size, and blood-pressure inputs.
- Supports partial scoring when users do not know every lab value.
- Explains each domain in plain language.
- Suggests practical next steps based on the lowest-scoring areas.
- Links newsletter signup to Substack instead of collecting emails directly.
- Includes an optional Ask Vital8 AI chat that can explain scores and prevention concepts when an OpenAI API key is configured.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

For local secrets, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`. The real secrets file is ignored by git.

## Streamlit Cloud

Deploy from this repository with:

- Main file: `app.py`
- Python dependencies: `requirements.txt`
- Optional secrets:

```toml
SUBSTACK_URL = "https://vital8.substack.com/"
OPENAI_API_KEY = "REPLACE_WITH_YOUR_OPENAI_API_KEY"
VITAL8_AI_MODEL = "gpt-5.5"
VITAL8_AI_MODEL_FALLBACKS = "gpt-5.4,gpt-5.4-mini"
VITAL8_AI_REASONING_EFFORT = "low"
```

The calculator works without an OpenAI key; the AI chat simply shows a setup message.

## Repository Privacy

This repository can be private while the Streamlit app remains publicly accessible. Keep real API keys only in Streamlit Secrets or local ignored files, never in committed code.

If a real API key was ever pasted into a public place, rotate it in the OpenAI dashboard before relying on it.

## Methods

The scoring details are documented in [docs/scoring-rationale.md](docs/scoring-rationale.md).

High-level notes:

- The final LE8-style score is the rounded average of known domain scores.
- Score categories are low below 50, moderate from 50-79, and high from 80-100.
- The diet score is an adapted consumer-facing estimate, not a full AHA dietary recall.
- The VO2max and biomarker layers are conceptual add-ons and are not validated clinical calculators.
- Ask Vital8 AI is educational only and uses guardrails for urgent symptoms and medication-change requests.

## Disclaimer

Vital8 is for education only. It does not diagnose, treat, or replace care from a clinician. If you have symptoms or urgent concerns, seek medical care.
