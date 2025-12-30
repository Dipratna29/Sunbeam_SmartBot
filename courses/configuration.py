from langchain.embeddings import init_embeddings
from langchain.chat_models import init_chat_model
import chromadb
import os
from dotenv import load_dotenv
load_dotenv()


def get_embedding_model():
   
    embed_model = init_embeddings(
        model="text-embedding-nomic-embed-text-v1.5",
        provider="openai",
        base_url="http://127.0.0.1:1234/v1",
        api_key="not-needed",
        check_embedding_ctx_length=False
    )

    return embed_model

def get_collection():
    db = chromadb.PersistentClient(path="G:/project/Sunbeam_SmartBot/courses_db")
    collection = db.get_or_create_collection(
        name="courses"
    )
        
    return collection    

def llm_config():
    api_key = os.getenv("GROQ_API_KEY")       
    llm = init_chat_model(
        model = "llama-3.3-70b-versatile",
        model_provider = "openai",
        base_url = "https://api.groq.com/openai/v1",
        api_key = api_key
    )   
    return llm