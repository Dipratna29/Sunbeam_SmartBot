import os
import shutil

from scraper_util import ScraperManager

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader


# STEP 1: SCRAPE DATA → TXT FILES
print(" Starting scraping process...")
manager = ScraperManager()
manager.scrape_all_to_txt()
manager.close()

print("All scraped data stored directly in TXT files")

# STEP 2: CONFIG
TEXT_FILES = [
    "text_data/sunbeam_about.txt",
    "text_data/sunbeam_internship.txt",
    "text_data/sunbeam_courses.txt"
]

CHROMA_DIR = "chroma_db"

# Remove old DB (avoid duplicate embeddings)
if os.path.exists(CHROMA_DIR):
    shutil.rmtree(CHROMA_DIR)
    print(" Old Chroma DB removed")


# STEP 3: EMBEDDING MODEL (NO DEPRECATION)
print(" Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# STEP 4: LOAD TXT DOCUMENTS
documents = []

for file_path in TEXT_FILES:
    loader = TextLoader(file_path, encoding="utf-8")
    documents.extend(loader.load())

print(f"Loaded {len(documents)} text documents")


# STEP 5: CHUNK TEXT
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n\n", "\n\n", "\n"],
    chunk_size=1200,
    chunk_overlap=150
)


chunks = text_splitter.split_documents(documents)
print(f" Created {len(chunks)} chunks")


# STORE EMBEDDINGS IN CHROMA
print(" Storing embeddings into Chroma DB...")

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=CHROMA_DIR
)

print(" Embeddings stored successfully in Chroma DB")
print(" FULL TXT → CHROMA PIPELINE COMPLETED")

