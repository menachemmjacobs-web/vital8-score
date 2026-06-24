"""Safe Streamlit chat UI for Vital8 AI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image

from content_library import (
    ADVANCED_INTERPRETATION_GUIDE,
    APPROVED_SCOPE,
    LE8_EVIDENCE_POSITIONING,
    LE8_DOMAIN_EXPLANATIONS,
    SCORING_METHODOLOGY,
)
from guardrails import detect_red_flags


# Configure the model here. Override with Streamlit secret VITAL8_AI_MODEL or env var if desired.
# Current high-quality default: GPT-5.5. Fallbacks keep the app usable if a project lacks model access.
DEFAULT_AI_MODEL = "gpt-5.5"
FALLBACK_MODELS = ["gpt-5.4", "gpt-5.4-mini"]
MAX_OUTPUT_TOKENS = 700
ICON_PATH = Path("assets/vital8-favicon.png")

SYSTEM_PROMPT = (
    "You are Vital8 AI, a science-based preventive cardiology coach for an educational Life's Essential 8 "
    "cardiovascular health calculator. Your style is an executive physiological briefing for a layperson: calm, "
    "confident, analytical, coaching-oriented, forward looking, and clear. Sound like a careful physician-teacher "
    "who can identify leverage without selling anything. Avoid alarmist language, excessive jargon, excessive "
    "bullets, and long disclaimers. Avoid em dashes. "
    "Explain the user's Vital8 score, major LE8 domains, and optional exploratory lenses such as VO2max, hsCRP, "
    "and Lp(a). Interpret systems rather than dumping raw data. Identify the highest-yield general prevention "
    "priority: the factor where the smallest realistic intervention could create the largest biological return. "
    "When useful, use this phrasing: 'The highest-yield action right now is...' "
    "You may discuss population-level evidence that higher LE8 and higher cardiorespiratory fitness are associated "
    "with longer life and more disease-free years, but do not estimate the user's personal life expectancy or promise "
    "a specific number of life years gained. Do not diagnose, treat, provide emergency triage, or recommend medication "
    "starts/stops/dose changes. Do not replace medical care. Do not claim Vital8 or its advanced layers are validated "
    "clinical risk calculators. If a user says alpha-lipoic acid while asking about the advanced lipid biomarker, "
    "gently clarify that Vital8 uses Lp(a), lipoprotein little-a, not the supplement alpha-lipoic acid. "
    "Keep most answers compact. Prefer short headers such as 'Current read', 'Why it matters', and 'Next move'. "
    "End with one practical follow-up question only when it would materially improve the next answer."
)


def _api_key() -> str | None:
    """Read OpenAI API key from Streamlit secrets first, then environment."""
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        secret_key = None
    return secret_key or os.environ.get("OPENAI_API_KEY")


def _model_name() -> str:
    try:
        secret_model = st.secrets.get("VITAL8_AI_MODEL")
    except Exception:
        secret_model = None
    return secret_model or os.environ.get("VITAL8_AI_MODEL", DEFAULT_AI_MODEL)


def _model_fallbacks() -> list[str]:
    configured = os.environ.get("VITAL8_AI_MODEL_FALLBACKS")
    try:
        secret_fallbacks = st.secrets.get("VITAL8_AI_MODEL_FALLBACKS")
    except Exception:
        secret_fallbacks = None
    raw = secret_fallbacks or configured
    if raw:
        return [item.strip() for item in str(raw).split(",") if item.strip()]
    return FALLBACK_MODELS


def _reasoning_effort() -> str:
    try:
        secret_effort = st.secrets.get("VITAL8_AI_REASONING_EFFORT")
    except Exception:
        secret_effort = None
    return secret_effort or os.environ.get("VITAL8_AI_REASONING_EFFORT", "low")


def _compact_context(score_summary: dict[str, Any] | None) -> str:
    summary = score_summary or {}
    context = {
        "score_summary": summary,
        "approved_scope": APPROVED_SCOPE,
        "scoring_methodology": SCORING_METHODOLOGY,
        "le8_evidence_positioning": LE8_EVIDENCE_POSITIONING,
        "advanced_interpretation_guide": ADVANCED_INTERPRETATION_GUIDE,
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
    last_error: Exception | None = None
    model_candidates = [_model_name()] + [model for model in _model_fallbacks() if model != _model_name()]
    for model in model_candidates:
        try:
            response = _create_response(client, model, user_payload, include_reasoning=True)
            return _response_text(response)
        except Exception as error:
            last_error = error
            if _should_retry_without_reasoning(error):
                try:
                    response = _create_response(client, model, user_payload, include_reasoning=False)
                    return _response_text(response)
                except Exception as retry_error:
                    last_error = retry_error
                    error = retry_error
            if not _should_try_next_model(error):
                raise
    if last_error:
        raise last_error
    return "I could not generate a response right now. Please try again in a moment."


def _create_response(client: Any, model: str, user_payload: str, include_reasoning: bool) -> Any:
    request: dict[str, Any] = {
        "model": model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_payload},
        ],
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }
    if include_reasoning:
        request["reasoning"] = {"effort": _reasoning_effort()}
    return client.responses.create(**request)


def _should_retry_without_reasoning(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)
    message = str(error).lower()
    return bool(status_code == 400 and ("reasoning" in message or "unsupported" in message))


def _should_try_next_model(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)
    message = str(error).lower()
    return bool(status_code in {400, 403, 404} or "model" in message or "permission" in message)


def _openai_error_message(error: Exception) -> str:
    status_code = getattr(error, "status_code", None)
    message = str(error).lower()

    if status_code == 401 or "invalid api key" in message or "incorrect api key" in message:
        return "The AI key looks invalid or revoked. Create a new OpenAI API key, add it to Streamlit Secrets, save, and reboot the app."
    if status_code == 403 or "permission" in message or "project" in message:
        return "The AI key is present, but this project may not have access to the selected model. Check the key's project permissions or set VITAL8_AI_MODEL to a model your project can use."
    if status_code == 404 or "model" in message:
        return "The selected AI model was not found for this API key. In Streamlit Secrets, try VITAL8_AI_MODEL = \"gpt-5.4-mini\" or another model available to your OpenAI project."
    if status_code == 429 or "quota" in message or "billing" in message:
        return "The AI key is present, but billing or quota may not be active for the OpenAI project. Check OpenAI billing/usage, then reboot the app."
    return "I could not reach the AI service right now. Check the Streamlit app logs for the OpenAI error, then try again."


def _ensure_chat_messages() -> None:
    if "vital8_chat_messages" not in st.session_state:
        st.session_state.vital8_chat_messages = [
            {
                "role": "assistant",
                "content": "Hi, I'm Vital8 AI. Ask me what your score means, where the biggest leverage is, or how VO2max and biomarkers change the interpretation. I keep this educational and practical, not diagnostic.",
            }
        ]


def _answer_user_message(score_summary: dict[str, Any] | None, user_message: str) -> None:
    api_key = _api_key()
    cleaned_message = user_message.strip()
    if not cleaned_message:
        return

    st.session_state.vital8_chat_messages.append({"role": "user", "content": cleaned_message})

    guardrail = detect_red_flags(cleaned_message)
    if guardrail["blocked"]:
        assistant_text = str(guardrail["message"])
    elif not api_key:
        assistant_text = "AI chat is not configured yet. Add an OpenAI API key to enable responses."
    else:
        try:
            assistant_text = _call_openai(api_key, score_summary, cleaned_message)
        except Exception as error:
            assistant_text = _openai_error_message(error)

    st.session_state.vital8_chat_messages.append({"role": "assistant", "content": assistant_text})


def _render_chat_messages(limit: int | None = None) -> None:
    messages = st.session_state.vital8_chat_messages
    shown_messages = messages[-limit:] if limit else messages
    if limit and len(messages) > limit:
        st.caption(f"Showing the most recent {limit} messages.")
    for message in shown_messages:
        avatar = Image.open(ICON_PATH) if message["role"] == "assistant" and ICON_PATH.exists() else None
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])


def render_chatbot(score_summary: dict[str, Any] | None) -> None:
    _ensure_chat_messages()
    api_key = _api_key()
    with st.container(key="vital8_ai_floating"):
        with st.popover("Ask Vital8 AI", use_container_width=True):
            st.subheader("Vital8 AI")
            st.caption(
                "Ask about your current entries, score, LE8 domains, VO2max, biomarkers, and prevention priorities. "
                "Educational only; not a substitute for medical care."
            )

            if not api_key:
                st.info(
                    "AI chat is not configured yet. Add OPENAI_API_KEY in Streamlit secrets or as a local environment variable to enable it."
                )

            with st.container(height=360, border=False):
                _render_chat_messages(limit=8)

            with st.form("vital8_ai_sidebar_form", clear_on_submit=True):
                user_message = st.text_area(
                    "Ask while you fill this out",
                    placeholder="Example: What is my highest-yield next move?",
                    height=90,
                    key="vital8_ai_sidebar_prompt",
                )
                submitted = st.form_submit_button("Ask Vital8 AI", use_container_width=True)

            if submitted:
                with st.spinner("Thinking..."):
                    _answer_user_message(score_summary, user_message)
                st.rerun()

            if st.button("Clear chat", key="clear_vital8_chat", use_container_width=True):
                del st.session_state.vital8_chat_messages
                _ensure_chat_messages()
                st.rerun()
