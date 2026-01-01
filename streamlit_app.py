import streamlit as st
from rag_chatbot import get_rag_answer
from app import run_data_pipeline

#PAGE CONFIG 
st.set_page_config(
    page_title="Sunbeam SmartBot",
    layout="wide"
)

#SESSION STATE
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

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

# Update vector DB
if st.sidebar.button("Update Data"):
    with st.spinner("Updating data..."):
        msg = run_data_pipeline()
        st.success(msg)

st.sidebar.divider()

#CHAT SELECTION 
chat_names = list(st.session_state.chats.keys())
selected_chat = st.sidebar.selectbox(
    "Select Chat",
    chat_names,
    index=chat_names.index(st.session_state.current_chat)
)
st.session_state.current_chat = selected_chat

# New Chat
if st.sidebar.button("New Chat"):
    new_name = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[new_name] = []
    st.session_state.current_chat = new_name
    st.rerun()

# Clear current chat
if st.sidebar.button("Clear Current Chat"):
    st.session_state.chats[st.session_state.current_chat] = []
    st.rerun()

# MAIN UI 
st.title("Good Evening")
st.subheader("How can I help you today?")

current_history = st.session_state.chats[st.session_state.current_chat]

#DISPLAY CHAT 
for role, message in current_history:
    with st.chat_message(role):
        st.markdown(message)

#USER INPUT
question = st.chat_input("Ask about Sunbeam...")

if question:
    # Save user message
    current_history.append(("user", question))
    with st.chat_message("user"):
        st.markdown(question)

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        with st.spinner("Thinking..."):
            for token in get_rag_answer(
                question=question,
                chat_history=current_history
            ):
                full_response += token
                placeholder.markdown(full_response)

    # Save assistant message
    current_history.append(("assistant", full_response))
