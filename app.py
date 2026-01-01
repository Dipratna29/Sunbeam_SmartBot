def run_data_pipeline():
    import os
    import shutil
    from scraper_util import ScraperManager
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import TextLoader

    TEXT_FILES = [
        "text_data/sunbeam_about.txt",
        "text_data/sunbeam_internship.txt",
        "text_data/sunbeam_courses.txt"
    ]

    CHROMA_DIR = "chroma_db"

    # 1️⃣ SCRAPE DATA
    manager = ScraperManager()
    manager.scrape_all_to_txt()
    manager.close()

    # 2️⃣ RESET DB
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)

    # 3️⃣ EMBEDDINGS
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    docs = []
    for file in TEXT_FILES:
        docs.extend(TextLoader(file, encoding="utf-8").load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(docs)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    return "✅ Data updated successfully"
