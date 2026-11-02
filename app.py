"""
Data pipeline: scrape sunbeaminfo.in -> text_data/*.txt -> Chroma index.

Command line:
    python app.py              # scrape the website, then rebuild the index
    python app.py --index-only # just rebuild the index from text_data/
"""

import shutil
import sys
import tempfile
from pathlib import Path

from config import TEXT_DATA_DIR, TEXT_FILES


def scrape_website():
    """
    Scrape into a temporary folder first and only replace text_data/
    when every scraper succeeded, so a failed or partial scrape never
    corrupts the existing data.
    """
    try:
        from scraper_util import ScraperManager
    except ImportError as e:
        raise RuntimeError(
            "Scraping needs Selenium + Chrome: "
            "pip install -r requirements-scraper.txt"
        ) from e

    tmp_dir = Path(tempfile.mkdtemp(prefix="sunbeam_scrape_"))
    try:
        with ScraperManager(output_dir=str(tmp_dir)) as manager:
            manager.scrape_all_to_txt()

        for target in TEXT_FILES:
            scraped = tmp_dir / target.name
            if not scraped.exists() or scraped.stat().st_size == 0:
                raise RuntimeError(f"Scrape produced no data for {target.name}")

        TEXT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        for target in TEXT_FILES:
            shutil.copyfile(tmp_dir / target.name, target)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def run_data_pipeline(scrape: bool = True) -> str:
    from vector_store import rebuild_index

    if scrape:
        scrape_website()
    n_chunks = rebuild_index()
    return f"✅ Data updated successfully ({n_chunks} chunks indexed)"


if __name__ == "__main__":
    index_only = "--index-only" in sys.argv
    print(run_data_pipeline(scrape=not index_only))
