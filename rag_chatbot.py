import streamlit as st
import time
import uuid
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="🤖 Sunbeam SmartBot (RAG)",
    page_icon="🤖",
    layout="wide"
)


# =====================================================
# LOAD ENV
# =====================================================
load_dotenv()


# =====================================================
# FULL THEME HANDLER (LIGHT + DARK)
# =====================================================
def apply_theme(theme):
    if theme == "dark":
        st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }

        section[data-testid="stSidebar"] { background-color: #161b22; }

        h1, h2, h3, h4, h5, h6, p, label, span {
            color: #fafafa !important;
        }

        .stButton > button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
        }

        textarea {
            background-color: #020617 !important;
            color: #fafafa !important;
        }

        div[data-testid="chat-message-user"] {
            background-color: #1e293b;
            border-radius: 12px;
            padding: 8px;
        }

        div[data-testid="chat-message-assistant"] {
            background-color: #020617;
            border-radius: 12px;
            padding: 8px;
        }

        div[data-testid="stExpander"] {
            background-color: #161b22;
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    else:  # LIGHT MODE
        st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #111827; }

        section[data-testid="stSidebar"] { background-color: #f3f4f6; }

        h1, h2, h3, h4, h5, h6, p, label, span {
            color: #111827 !important;
        }

        .stButton > button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
        }

        textarea {
            background-color: #f9fafb !important;
            color: #111827 !important;
        }

        div[data-testid="chat-message-user"] {
            background-color: #e0e7ff;
            border-radius: 12px;
            padding: 8px;
        }

        div[data-testid="chat-message-assistant"] {
            background-color: #f9fafb;
            border-radius: 12px;
            padding: 8px;
        }

        div[data-testid="stExpander"] {
            background-color: #f3f4f6;
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)


# =====================================================
# SESSION STATE INIT
# =====================================================
if "chats" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.chats = {
        chat_id: {"title": "New Chat", "messages": []}
    }
    st.session_state.active_chat = chat_id

if "theme" not in st.session_state:
    st.session_state.theme = "light"


# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.title("⚙️ SmartBot Controls")

    st.markdown("### 🌗 Theme")
    st.session_state.theme = st.radio(
        "Select Theme",
        ["light", "dark"],
        index=0 if st.session_state.theme == "light" else 1,
        horizontal=True
    )

    apply_theme(st.session_state.theme)

    st.markdown("### 💬 Chats")

    if st.button("➕ New Chat", type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {
            "title": "New Chat",
            "messages": []
        }
        st.session_state.active_chat = new_id
        st.rerun()

    chat_titles = {
        cid: data["title"]
        for cid, data in st.session_state.chats.items()
    }

    st.session_state.active_chat = st.radio(
        "Previous Chats",
        options=list(chat_titles.keys()),
        format_func=lambda x: chat_titles[x]
    )

    if st.button("🧹 Clear Current Chat"):
        st.session_state.chats[st.session_state.active_chat]["messages"] = []
        st.rerun()

    st.markdown("### 🔧 Model Settings")
    temperature = st.slider("LLM Temperature", 0.0, 1.0, 0.1, 0.05)

    show_context = st.toggle("🔍 Show Retrieved Context", value=False)

    st.markdown("---")
    st.markdown("""
    **Sunbeam SmartBot**  
    Retrieval-Augmented Generation  
    ✔ No hallucinations  
    ✔ Context-only answers
    """)


# =====================================================
# CONFIG
# =====================================================
CHROMA_DIR = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# =====================================================
# EMBEDDINGS
# =====================================================
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)


# =====================================================
# VECTOR DB
# =====================================================
vector_db = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings
)


# =====================================================
# RETRIEVER
# =====================================================
retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 15, "fetch_k": 40}
)


# =====================================================
# LLM
# =====================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=temperature
)


# =====================================================
# PROMPTS
# =====================================================
SYSTEM_PROMPT = """
You are an AI Assistant powered by Retrieval-Augmented Generation (RAG).
Answer ONLY using the provided context.
"""

USER_PROMPT = """
CONTEXT:
{context}

QUESTION:
{question}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", USER_PROMPT),
])


# =====================================================
# STREAMING EFFECT
# =====================================================
def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.03)


# =====================================================
# RAG FUNCTION
# =====================================================
def rag_answer(question: str):
    docs = retriever.invoke(question)

    if not docs:
        return "I don’t have enough information to answer that based on the available data.", ""

    context = "\n\n".join(doc.page_content for doc in docs)
    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "question": question
    })

    return answer, context


# =====================================================
# CHAT UI
# =====================================================
st.title("🤖 Sunbeam SmartBot")
st.caption("Ask about courses, fees, internships, batches & more")

current_chat = st.session_state.chats[st.session_state.active_chat]

for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


user_input = st.chat_input("Ask your question here...")

if user_input:
    current_chat["messages"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, context = rag_answer(user_input)
            st.write_stream(stream_text(answer))

        if show_context:
            with st.expander("📄 Retrieved Context"):
                st.markdown(context)

    current_chat["messages"].append(
        {"role": "assistant", "content": answer}
    )

    if current_chat["title"] == "New Chat":
        current_chat["title"] = user_input[:30]
