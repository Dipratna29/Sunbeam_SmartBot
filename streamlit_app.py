import hmac
import logging
from datetime import datetime

import streamlit as st

from config import get_setting
from rag_chatbot import IST, get_rag_answer
from vector_store import ensure_index

logging.basicConfig(level=logging.INFO)

#PAGE CONFIG
st.set_page_config(
    page_title="Sunbeam SmartBot",
    layout="wide"
)


# KNOWLEDGE BASE (built once per server process, rebuilt if text_data changes)
@st.cache_resource(show_spinner="Preparing the Sunbeam knowledge base (first start can take a minute)...")
def _init_knowledge_base():
    ensure_index()
    return True


try:
    _init_knowledge_base()
except Exception as e:
    logging.exception("Knowledge base failed to load")
    st.error(f"Could not load the knowledge base: {e}")
    st.stop()

if not get_setting("GROQ_API_KEY"):
    st.warning(
        "GROQ_API_KEY is not configured. Add it to `.env` (local) or the "
        "app's Secrets (Streamlit Cloud) so the bot can answer."
    )

#SESSION STATE
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"


def _new_chat():
    n = len(st.session_state.chats) + 1
    while f"Chat {n}" in st.session_state.chats:
        n += 1
    name = f"Chat {n}"
    st.session_state.chats[name] = []
    st.session_state.current_chat = name


def _clear_chat():
    st.session_state.chats[st.session_state.current_chat] = []


# SIDEBAR
st.sidebar.title("Sunbeam SmartBot")
st.sidebar.caption("AI Assistant for Sunbeam Institute")

st.sidebar.markdown("""
You can ask about:
- Courses & syllabus
- Internship programs
- Batch schedules
- Fees & duration
- Eligibility & prerequisites
""")

st.sidebar.divider()

#CHAT SELECTION (widget is bound to session_state.current_chat)
st.sidebar.selectbox(
    "Select Chat",
    list(st.session_state.chats.keys()),
    key="current_chat",
)

st.sidebar.button("New Chat", on_click=_new_chat)
st.sidebar.button("Clear Current Chat", on_click=_clear_chat)

# ADMIN: re-scrape website + rebuild index.
# Only shown when ADMIN_PASSWORD is set, so public visitors can't trigger it.
admin_password = get_setting("ADMIN_PASSWORD")
if admin_password:
    with st.sidebar.expander("Admin: Update Data"):
        entered = st.text_input("Admin password", type="password")
        scrape = st.checkbox(
            "Re-scrape sunbeaminfo.in (needs Chrome + Selenium)", value=True
        )
        if st.button("Update Data"):
            if not hmac.compare_digest(entered.encode(), admin_password.encode()):
                st.error("Wrong password.")
            else:
                from app import run_data_pipeline

                with st.spinner("Updating data..."):
                    try:
                        st.success(run_data_pipeline(scrape=scrape))
                    except Exception as e:
                        logging.exception("Data update failed")
                        st.error(f"Update failed, existing data kept: {e}")

# MAIN UI
hour = datetime.now(IST).hour
greeting = (
    "Good Morning" if 5 <= hour < 12
    else "Good Afternoon" if 12 <= hour < 17
    else "Good Evening"
)
st.title(greeting)
st.subheader("How can I help you today?")

current_history = st.session_state.chats[st.session_state.current_chat]

#DISPLAY CHAT
for role, message in current_history:
    with st.chat_message(role):
        st.markdown(message)

#USER INPUT
question = st.chat_input("Ask about Sunbeam...")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")
        full_response = ""

        # history passed WITHOUT the current question (it is sent separately)
        for token in get_rag_answer(
            question=question,
            chat_history=list(current_history)
        ):
            full_response += token
            placeholder.markdown(full_response)

        if not full_response.strip():
            full_response = "I don't have that information."
            placeholder.markdown(full_response)

    # Save both messages
    current_history.append(("user", question))
    current_history.append(("assistant", full_response))
