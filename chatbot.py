"""Safe Streamlit chat UI for Vital8 AI."""

from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

from content_library import APPROVED_SCOPE, LE8_DOMAIN_EXPLANATIONS
from guardrails import detect_red_flags


# Configure the model here. Override with VITAL8_AI_MODEL if desired.
AI_MODEL = os.environ.get("VITAL8_AI_MODEL", "gpt-5-mini")
MAX_OUTPUT_TOKENS = 450

SYSTEM_PROMPT = (
    "You are Vital8 AI, an educational assistant for a Life's Essential 8 cardiovascular health calculator. "
    "Explain results in plain language, identify general prevention priorities, and help users prepare better "
    "questions for their clinician. Do not diagnose, treat, provide emergency triage, or recommend medication "
    "changes. Do not replace medical care. Do not claim Vital8 is a validated clinical risk calculator. "
    "Keep answers concise and practical. Every answer should generally include: what this means, one practical "
    "next step, and what to discuss with a clinician if relevant."
)


def _api_key() -> str | None:
    """Read OpenAI API key from Streamlit secrets first, then environment."""
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        secret_key = None
    return secret_key or os.environ.get("OPENAI_API_KEY")


def _compact_context(score_summary: dict[str, Any] | None) -> str:
    summary = score_summary or {}
    context = {
        "score_summary": summary,
        "approved_scope": APPROVED_SCOPE,
        "domain_explanations": LE8_DOMAIN_EXPLANATIONS,
    }
    return json.dumps(context, ensure_ascii=True, separators=(",", ":"))


def _response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text.strip()
    try:
        return response.output[0].content[0].text.strip()
    except Exception:
        return "I could not generate a response right now. Please try again in a moment."


def _call_openai(api_key: str, score_summary: dict[str, Any] | None, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    user_payload = (
        "Use this compact Vital8 context and answer the user's latest question only.\n"
        f"Context JSON: {_compact_context(score_summary)}\n"
        f"User question: {user_message}"
    )
    response = client.responses.create(
        model=AI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_payload},
        ],
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )
    return _response_text(response)


def render_chatbot(score_summary: dict[str, Any] | None) -> None:
    st.divider()
    st.header("Ask Vital8 AI")
    st.caption(
        "Ask general questions about your Vital8 score, Life's Essential 8, prevention priorities, "
        "or what to discuss with your clinician. This is educational only and does not replace medical care."
    )

    if "vital8_chat_messages" not in st.session_state:
        st.session_state.vital8_chat_messages = [
            {
                "role": "assistant",
                "content": "Hi, I'm Vital8 AI. I can explain your score, LE8 domains, and general prevention priorities. I cannot diagnose symptoms, triage emergencies, or advise medication changes.",
            }
        ]

    for message in st.session_state.vital8_chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    api_key = _api_key()
    if not api_key:
        st.info(
            "AI chat is not configured yet. Add OPENAI_API_KEY in Streamlit secrets or as a local environment variable to enable it."
        )

    user_message = st.chat_input("Ask about your Vital8 score or Life's Essential 8")
    if not user_message:
        return

    st.session_state.vital8_chat_messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.write(user_message)

    guardrail = detect_red_flags(user_message)
    if guardrail["blocked"]:
        assistant_text = str(guardrail["message"])
    elif not api_key:
        assistant_text = "AI chat is not configured yet. Add an OpenAI API key to enable responses."
    else:
        try:
            assistant_text = _call_openai(api_key, score_summary, user_message)
        except Exception:
            assistant_text = "I could not reach the AI service right now. Please try again later."

    st.session_state.vital8_chat_messages.append({"role": "assistant", "content": assistant_text})
    with st.chat_message("assistant"):
        st.write(assistant_text)
