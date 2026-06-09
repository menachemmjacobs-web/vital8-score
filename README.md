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
5. Add the Substack URL secret below if you want the newsletter button to point to your publication. A local template is included at `.streamlit/secrets.toml.example`.

## Link newsletter signup to Substack

The app does not collect newsletter emails. The newsletter button sends visitors to Substack, where Substack handles the email signup.

In Streamlit Cloud, open your app settings and add:

```toml
SUBSTACK_URL = "https://vital8.substack.com/"
```

For local testing, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in the real Substack URL. The real `secrets.toml` is ignored by git.

## Notes

- The final score is the unweighted average of available component scores.
- Score ranges follow the LE8 framing used in the app: low below 50, moderate 50-79, high 80-100.
- If lipids, glucose, or blood pressure are missing, the app calculates a partial score.
- The diet score is a simplified MVP estimate based on the user's average pattern over the past month. It is not the full AHA diet algorithm.
- The optional Vital8 Advanced layer keeps LE8 unchanged, then adds a conceptual hsCRP/Lp(a) "biological drag" estimate. hsCRP is treated as a potentially modifiable inflammatory signal; Lp(a) is treated as a largely genetic risk signal. This is an exploratory prototype, not a validated clinical calculator.
- Newsletter signup is handled by Substack through an outbound link. This app does not store newsletter emails.

## Disclaimer

This tool is for education only and does not diagnose, treat, or replace care from your clinician. If you have symptoms or urgent concerns, seek medical care.
