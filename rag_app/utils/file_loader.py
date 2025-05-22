import os
from langchain_community.document_loaders import PyPDFLoader

def list_pdfs(folder_path: str) -> list[str]:
    """
    Recursively list all PDF files in the given folder.

    :param folder_path: Path to the parent folder.
    :return: List of full filepaths to .pdf files.
    """
    pdf_files = []
    for root, _, files in os.walk(folder_path):
        for fname in files:
            if fname.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, fname))
    assert len(pdf_files) > 0, f"No PDF files found in {folder_path}"
    return pdf_files


def load_pdf_text(filepath: str, max_pages: int = 10) -> str:
    """
    Load and extract text from the first `max_pages` pages of a PDF file using LangChain's PyPDFLoader.

    :param filepath: Path to the PDF file.
    :param max_pages: Maximum number of pages to read (default: 10).
    :return: Extracted text as a single string.
    """
    text_chunks = []
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    for page in docs[:max_pages]:
        text_chunks.append(page.page_content)
    return "\n".join(text_chunks)


def ingest_folder(folder_path: str, max_pages: int = 10) -> dict[str, str]:
    """
    Ingest all PDFs in a folder and return a mapping of filename to extracted text.

    :param folder_path: Path to the folder containing PDFs.
    :param max_pages: Pages to load per PDF.
    :return: Dict where key is filename and value is extracted text.
    """
    pdf_paths = list_pdfs(folder_path)
    corpus = {}
    for path in pdf_paths:
        fname = os.path.basename(path)
        try:
            corpus[fname] = load_pdf_text(path, max_pages=max_pages)
        except Exception as e:
            corpus[fname] = f"ERROR_LOADING_FILE: {e}"
    return corpus
