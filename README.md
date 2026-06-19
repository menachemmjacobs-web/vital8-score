# Vital8 Heart Health Score

A small Streamlit prototype for an adult Life's Essential 8 cardiovascular health score. It presents the assessment as one continuous scroll, collects lifestyle and measurement inputs, calculates a 0-100 score, shows component scores, creates charts, and suggests next steps.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create a new app from the repository.
3. Set the entrypoint to `app.py`.
4. Confirm `requirements.txt` is detected.
5. Add the Substack URL and OpenAI API key secrets below if you want the newsletter button and AI chat enabled. A local template is included at `.streamlit/secrets.toml.example`.

## Link newsletter signup to Substack

The app does not collect newsletter emails. The newsletter button sends visitors to Substack, where Substack handles the email signup.

In Streamlit Cloud, open your app settings and add:

```toml
SUBSTACK_URL = "https://vital8.substack.com/"
```

For local testing, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in the real Substack URL. The real `secrets.toml` is ignored by git.

## Enable Ask Vital8 AI

The calculator works without an OpenAI API key. If no key is configured, the AI chat section shows a setup message instead of crashing.

For local testing, either add this to `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

or export an environment variable before starting Streamlit:

```bash
export OPENAI_API_KEY="sk-your-key-here"
streamlit run app.py
```

In Streamlit Cloud, open the app settings, go to Secrets, and add:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

The default model is configured in `chatbot.py` as `gpt-5-mini`. You can override it locally with:

```bash
export VITAL8_AI_MODEL="gpt-5-mini"
```

## Notes

- The final score is the unweighted average of available component scores.
- Score ranges follow the LE8 framing used in the app: low below 50, moderate 50-79, high 80-100.
- If lipids, glucose, or blood pressure are missing, the app calculates a partial score.
- The diet score is an adapted consumer-facing estimate that uses eight LE8-aligned food-pattern questions. It is not the full AHA diet algorithm or a validated dietary recall.
- The optional Vital8 Fitness layer keeps LE8 unchanged, then adds a conceptual VO2max/cardiorespiratory fitness modifier. This is exploratory and not a validated clinical calculator.
- The optional Vital8 Advanced layer keeps LE8 unchanged, then adds a conceptual hsCRP/Lp(a) "biological drag" estimate. hsCRP is treated as a potentially modifiable inflammatory signal; Lp(a) is treated as a largely genetic risk signal. This is an exploratory prototype, not a validated clinical calculator.
- Ask Vital8 AI is educational only. It uses rule-based guardrails to block urgent symptoms and medication-change requests before any OpenAI API call.
- Newsletter signup is handled by Substack through an outbound link. This app does not store newsletter emails.

## Disclaimer

This tool is for education only and does not diagnose, treat, or replace care from your clinician. If you have symptoms or urgent concerns, seek medical care.
