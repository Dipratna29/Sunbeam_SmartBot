"""
Vector store helpers: one shared embedding model + Chroma DB per process,
and an index that rebuilds itself whenever text_data/ changes.
"""

import hashlib
import json
import threading
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBED_MODEL,
    INDEX_META_FILE,
    TEXT_FILES,
)
from loaders.sunbeam_txt_loader import SunbeamTXTLoader

_index_lock = threading.Lock()


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


@lru_cache(maxsize=1)
def get_vector_db():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


def _source_fingerprint() -> str:
    """Hash of the text files + settings that shape the index."""
    h = hashlib.sha256()
    h.update(f"{EMBED_MODEL}|{CHUNK_SIZE}|{CHUNK_OVERLAP}".encode())
    for path in TEXT_FILES:
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def _read_meta() -> dict:
    try:
        return json.loads(INDEX_META_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_chunks():
    missing = [str(p) for p in TEXT_FILES if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing data files: " + ", ".join(missing)
            + ". Run `python app.py` to scrape them."
        )

    docs = []
    for path in TEXT_FILES:
        docs.extend(SunbeamTXTLoader(str(path)).load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(docs)


def rebuild_index() -> int:
    """
    Re-embed all text files into the existing collection.

    Clears the collection through Chroma's API instead of deleting the
    folder, so it works while the app has the DB open (and on Windows,
    where an open DB file can't be deleted).
    """
    with _index_lock:
        chunks = _load_chunks()
        db = get_vector_db()

        existing_ids = db.get(include=[])["ids"]
        if existing_ids:
            db.delete(ids=existing_ids)

        db.add_documents(chunks)

        INDEX_META_FILE.write_text(
            json.dumps({"fingerprint": _source_fingerprint(),
                        "chunks": len(chunks)}),
            encoding="utf-8",
        )
        return len(chunks)


def ensure_index() -> bool:
    """Build the index if it is empty or out of date. Returns True if rebuilt."""
    db = get_vector_db()
    up_to_date = (
        _read_meta().get("fingerprint") == _source_fingerprint()
        and len(db.get(include=[])["ids"]) > 0
    )
    if up_to_date:
        return False
    rebuild_index()
    return True
