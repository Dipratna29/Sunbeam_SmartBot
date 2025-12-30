# from test import run_modular_courses_scraper

# print(run_modular_courses_scraper())

from configuration import get_embedding_model, get_collection, llm_config
import streamlit as st


# def course_chatbot():
st.title("🎓 Sunbeam Courses SmartBot")

query_text = st.chat_input("Ask about courses, syllabus, fees, duration...")

if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "system", "content": "You are an expert course advisor for Sunbeam."}
    ]

if query_text:
    st.session_state.conversation.append({
        "role": "user",
        "content": query_text
    })

    embed_model = get_embedding_model()
    collection = get_collection()

    # 🔹 Embed query
    query_embedding = embed_model.embed_query(query_text)

    # 🔹 Query vector DB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["documents", "metadatas"]
    )

    if not results["documents"] or not results["documents"][0]:
        st.error("No relevant course found.")
    

    # 🔹 Prepare context for LLM
    course_context = []
    for i in range(len(results["documents"][0])):
        meta = results["metadatas"][0][i]

        course_context.append(f"""
Course Title: {meta.get("course_title", "N/A")}
Section: {meta.get("section", "N/A")}
URL: {meta.get("url", "N/A")}

Content:
{results["documents"][0][i]}
""")

    context_text = "\n\n---\n\n".join(course_context)

    # 🔹 LLM Prompt
    llm_prompt = f"""
You are a professional course advisor.

User Query:
{query_text}

Use ONLY the information below to answer.
Be concise, accurate, and helpful.
If fees, duration, or eligibility is asked — mention clearly.

Course Data:
{context_text}

Answer:
"""

    llm = llm_config()
    answer = llm.invoke(llm_prompt)

    st.session_state.conversation.append({
        "role": "assistant",
        "content": answer.content
    })

# 🔹 Render chat history
for msg in st.session_state.conversation:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

