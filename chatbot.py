"""Safe Streamlit chat UI for Vital8 AI."""

from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

from content_library import APPROVED_SCOPE, LE8_DOMAIN_EXPLANATIONS
from guardrails import detect_red_flags


# Configure the model here. Override with Streamlit secret VITAL8_AI_MODEL or env var if desired.
# Current high-quality default: GPT-5.5. Fallbacks keep the app usable if a project lacks model access.
DEFAULT_AI_MODEL = "gpt-5.5"
FALLBACK_MODELS = ["gpt-5.4", "gpt-5.4-mini"]
MAX_OUTPUT_TOKENS = 700

SYSTEM_PROMPT = (
    "You are Vital8 AI, a science-based preventive cardiology coach for an educational Life's Essential 8 "
    "cardiovascular health calculator. Your tone is warm, intelligent, practical, and plain-language: like a "
    "careful physician-teacher helping someone understand prevention without selling them anything. "
    "Explain the user's Vital8 score, major LE8 domains, and optional exploratory lenses such as VO2max, hsCRP, "
    "and Lp(a). Identify the highest-yield general prevention priorities and help users prepare better questions "
    "for their clinician. You may discuss population-level evidence that higher LE8 and higher cardiorespiratory "
    "fitness are associated with longer life and more disease-free years, but do not estimate the user's personal "
    "life expectancy or promise a specific number of life years gained. Do not diagnose, treat, provide emergency "
    "triage, or recommend medication starts/stops/dose changes. Do not replace medical care. Do not claim Vital8 "
    "or its advanced layers are validated clinical risk calculators. Keep answers concise, practical, and grounded. "
    "Structure most answers as: what this means, what to work on first, and what to discuss with a clinician."
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


def render_chatbot(score_summary: dict[str, Any] | None) -> None:
    st.divider()
    st.header("Ask Vital8 AI")
    st.caption(
        "Ask general questions about your Vital8 score, Life's Essential 8, VO2max, biomarkers, prevention priorities, "
        "or what to discuss with your clinician. This is educational only and does not replace medical care."
    )

    if "vital8_chat_messages" not in st.session_state:
        st.session_state.vital8_chat_messages = [
            {
                "role": "assistant",
                "content": "Hi, I'm Vital8 AI. I can explain your score, LE8 domains, VO2max, biomarkers, and general prevention priorities. I cannot diagnose symptoms, triage emergencies, or advise medication changes.",
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
        except Exception as error:
            assistant_text = _openai_error_message(error)

    st.session_state.vital8_chat_messages.append({"role": "assistant", "content": assistant_text})
    with st.chat_message("assistant"):
        st.write(assistant_text)
