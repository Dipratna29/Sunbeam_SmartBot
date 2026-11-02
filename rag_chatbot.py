import logging
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_MODEL, RETRIEVER_FETCH_K, RETRIEVER_K, get_setting
from vector_store import get_vector_db

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
NO_INFO = "I don't have that information."

PROMPT = ChatPromptTemplate.from_template(
    """
You are Sunbeam SmartBot - an AI assistant for Sunbeam Institute.

Today's date: {today}

RULES:
- Use ONLY the provided context.
- Use conversation history to understand follow-up questions.
- Do NOT hallucinate.
- If information is missing, say:
"I don't have that information."
- Batch schedules come from a saved copy of the website. If a batch's
  start date is before today's date, say it may already have started or
  finished and suggest checking https://www.sunbeaminfo.in for current batches.

Conversation History:
{conversation}

Context:
{context}

User Question:
{question}

Answer:
"""
)


class MissingAPIKeyError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _get_llm():
    from langchain_groq import ChatGroq

    api_key = get_setting("GROQ_API_KEY")
    if not api_key:
        raise MissingAPIKeyError(
            "GROQ_API_KEY is not set. Add it to `.env` (local) or to the "
            "app's Secrets (Streamlit Cloud)."
        )
    return ChatGroq(
        model=GROQ_MODEL,
        temperature=0.2,
        api_key=api_key,
        streaming=True,
    )


def _get_retriever():
    return get_vector_db().as_retriever(
        search_type="mmr",
        search_kwargs={"k": RETRIEVER_K, "fetch_k": RETRIEVER_FETCH_K},
    )


def get_rag_answer(question: str, chat_history: list):
    """
    STREAMING RAG-based answer using Chroma + Groq LLM.

    `chat_history` = earlier (role, message) turns, NOT including `question`.
    """

    # CONVERSATION HISTORY
    conversation = ""
    for role, msg in chat_history[-6:]:
        speaker = "User" if role == "user" else "Assistant"
        conversation += f"{speaker}: {msg}\n"

    # For follow-ups ("what are its fees?") also search with the
    # previous user question so retrieval finds the right course.
    previous_user_msgs = [m for r, m in chat_history if r == "user"]
    search_query = question
    if previous_user_msgs:
        search_query = f"{previous_user_msgs[-1]}\n{question}"

    try:
        docs = _get_retriever().invoke(search_query)
    except Exception:
        logger.exception("Retrieval failed")
        yield "⚠️ Could not search the knowledge base. Please try again."
        return

    if not docs:
        yield NO_INFO
        return

    context = "\n\n".join(doc.page_content for doc in docs)

    try:
        chain = PROMPT | _get_llm() | StrOutputParser()
        for chunk in chain.stream({
            "today": datetime.now(IST).strftime("%d-%b-%Y"),
            "conversation": conversation or "(none)",
            "context": context,
            "question": question,
        }):
            yield chunk
    except MissingAPIKeyError as e:
        yield f"⚠️ {e}"
    except Exception as e:
        logger.exception("Groq LLM call failed")
        yield (
            "⚠️ The language model request failed "
            f"({type(e).__name__}: {e}). Check GROQ_API_KEY and that "
            f"GROQ_MODEL='{GROQ_MODEL}' is still offered by Groq."
        )
