# Sunbeam SmartBot

A RAG chatbot that answers questions about [Sunbeam Institute](https://www.sunbeaminfo.in): courses, syllabus, batch schedules, internships and prerequisites.

**Stack:** Streamlit UI · LangChain · Chroma vector DB · `all-MiniLM-L6-v2` embeddings · Groq LLM (`openai/gpt-oss-120b`) · Selenium scrapers

```
sunbeaminfo.in ──(Selenium scrapers)──► text_data/*.txt ──(embeddings)──► chroma_db/ ──► RAG + Groq ──► Streamlit chat
```

## Project layout

| Path | Purpose |
|---|---|
| `streamlit_app.py` | Chat UI (entry point) |
| `rag_chatbot.py` | Retrieval + Groq LLM streaming answer |
| `vector_store.py` | Embeddings, Chroma DB, auto-rebuilding index |
| `config.py` | Settings (env vars / Streamlit secrets) |
| `app.py` | Data pipeline: scrape → text files → index (also a CLI) |
| `scraper_util.py`, `scrapers/` | Selenium scrapers for each page |
| `text_data/` | Scraped website text (committed, this is the knowledge base) |
| `chroma_db/` | Generated vector index (git-ignored, built automatically) |

## Run locally

Python 3.11 or 3.12 recommended.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
copy .env.example .env         # Windows   (cp on macOS/Linux)
# edit .env and set GROQ_API_KEY (free key: https://console.groq.com/keys)

streamlit run streamlit_app.py
```

On first start the app downloads the embedding model and builds `chroma_db/` from `text_data/` (about a minute). After that it only rebuilds when the text files change.

## Refresh the data (re-scrape the website)

Scraping needs Google Chrome installed and is best done on your own machine:

```bash
pip install -r requirements-scraper.txt
python app.py               # scrape sunbeaminfo.in + rebuild the index
python app.py --index-only  # only rebuild the index from text_data/
```

Scraping writes to a temporary folder and only replaces `text_data/` if every page succeeded, so a failed scrape never damages existing data. Commit the updated `text_data/` and the deployed app re-indexes automatically on its next start.

To get an **Admin: Update Data** panel in the app sidebar, set `ADMIN_PASSWORD` in `.env` / secrets. Without it the panel is hidden so public visitors can't trigger scraping.

## Deploy

### Streamlit Community Cloud (easiest)

1. Push this repo to GitHub (`.env` and `chroma_db/` are git-ignored).
2. On [share.streamlit.io](https://share.streamlit.io) create an app: main file `streamlit_app.py`, Python 3.12 (Advanced settings).
3. In **Advanced settings → Secrets** paste:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
4. Deploy. The first boot installs PyTorch and builds the index, so allow a few minutes.

### Docker (Render, Railway, Hugging Face Spaces, any VM)

```bash
docker build -t sunbeam-smartbot .
docker run -p 8501:8501 -e GROQ_API_KEY=gsk_... sunbeam-smartbot
```

The image uses CPU-only PyTorch and pre-builds the index at build time. It listens on `$PORT` if the platform sets one (default 8501).

## Configuration

| Setting | Required | Default | Notes |
|---|---|---|---|
| `GROQ_API_KEY` | yes | none | Groq API key |
| `GROQ_MODEL` | no | `openai/gpt-oss-120b` | Change if Groq retires the model |
| `ADMIN_PASSWORD` | no | none | Enables the in-app data update panel |
| `EMBED_MODEL` | no | `sentence-transformers/all-MiniLM-L6-v2` | Changing it triggers a re-index |

## Troubleshooting

- **"The language model request failed … model_decommissioned"**: Groq retired the model. Set `GROQ_MODEL` to a current one from [console.groq.com/docs/models](https://console.groq.com/docs/models).
- **Chroma error after upgrading packages**: delete the `chroma_db/` folder; it is rebuilt on the next start.
- **`sqlite3` version error from Chroma on an old Linux host**: add `pysqlite3-binary` to requirements and put `__import__("pysqlite3"); import sys; sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")` at the top of `streamlit_app.py`.
- **A scraper fails**: the site's HTML changed. Course scrapers rely on fixed accordion IDs (e.g. `#collapse128`), so update the ID in the matching `scrapers/coursesN.py`.
