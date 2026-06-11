"""
Shared API key utilities for OpenRouter services.
"""

import os


def get_openrouter_api_key() -> str:
    """Get OpenRouter API key from environment or Streamlit session state."""
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    import streamlit as st
    try:
        if "openrouter_api_key" in st.session_state and st.session_state["openrouter_api_key"]:
            key = st.session_state["openrouter_api_key"].strip()
            if key.startswith("sk-or-v1-"):
                return key
            else:
                st.session_state["openrouter_api_key"] = ""
    except Exception:
        pass
    return ""
