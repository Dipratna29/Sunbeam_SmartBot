"""
Central configuration for Sunbeam SmartBot.

Settings are read from (in order):
  1. Environment variables / a local `.env` file
  2. Streamlit secrets (`.streamlit/secrets.toml` or the Streamlit Cloud
     "Secrets" box)
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_setting(name: str, default=None):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        # No secrets file, or not running inside Streamlit
        pass
    return default


# ---------------- PATHS ----------------
TEXT_DATA_DIR = BASE_DIR / "text_data"
CHROMA_DIR = BASE_DIR / "chroma_db"
INDEX_META_FILE = CHROMA_DIR / "sunbeam_index.json"

TEXT_FILES = [
    TEXT_DATA_DIR / "sunbeam_about.txt",
    TEXT_DATA_DIR / "sunbeam_internship.txt",
    TEXT_DATA_DIR / "sunbeam_courses.txt",
]

# ---------------- MODELS ----------------
EMBED_MODEL = get_setting(
    "EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# llama-3.3-70b-versatile was shut down by Groq on 16 Aug 2026.
# Override with GROQ_MODEL if Groq retires this one too.
GROQ_MODEL = get_setting("GROQ_MODEL", "openai/gpt-oss-120b")

# ---------------- CHUNKING / RETRIEVAL ----------------
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
RETRIEVER_K = 10
RETRIEVER_FETCH_K = 20
