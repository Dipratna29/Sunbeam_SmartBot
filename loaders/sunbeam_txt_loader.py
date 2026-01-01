from typing import Iterator
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader


class SunbeamTXTLoader(BaseLoader):
    """
    Loads Sunbeam TXT files and yields LangChain Documents
    """

    def __init__(self, txt_path: str):
        self.txt_path = txt_path

    def lazy_load(self) -> Iterator[Document]:
        with open(self.txt_path, "r", encoding="utf-8") as f:
            content = f.read()

        yield Document(
            page_content=content,
            metadata={
                "source": self.txt_path,
                "type": "text"
            }
        )
