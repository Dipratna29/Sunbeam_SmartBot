import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# LOAD ENV VARIABLES
load_dotenv()

CHROMA_DIR = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_rag_answer(question: str, chat_history: list):
    """
    STREAMING RAG-based answer using Chroma + Groq LLM
    """

    #CONVERSATION HISTORY
    conversation = ""
    for role, msg in chat_history[-6:]:
        if role == "user":
            conversation += f"User: {msg}\n"
        else:
            conversation += f"Assistant: {msg}\n"

    #EMBEDDINGS 
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    # VECTOR DB
    vector_db = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    retriever = vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 20}
    )

    # GROQ LLM (STREAM ENABLED) 
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
        streaming=True
    )

    # PROMPT 
    prompt = ChatPromptTemplate.from_template(
        """
You are Sunbeam SmartBot - an AI assistant for Sunbeam Institute.

RULES:
- Use ONLY the provided context.
- Use conversation history to understand follow-up questions.
- Do NOT hallucinate.
- If information is missing, say:
"I don't have that information."

Conversation History:
{conversation}

Context:
{context}

User Question:
{question}

Answer:
"""
    )

    # RETRIEVE CONTEXT
    docs = retriever.invoke(question)

    if not docs:
        yield "I don't have that information."
        return

    context = "\n\n".join(doc.page_content for doc in docs)

    # RAG CHAIN 
    chain = prompt | llm | StrOutputParser()

    try:
        for chunk in chain.stream({
            "conversation": conversation,
            "context": context,
            "question": question
        }):
            yield chunk
    except Exception:
        yield " Unable to connect to Groq LLM. Please check API key."
