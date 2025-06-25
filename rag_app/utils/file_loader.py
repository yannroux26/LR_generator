import os
import json
from langchain_community.document_loaders import PyPDFLoader
from .section_splitterv2 import extract_specific_sections

def load_pdf_text(filepath: str, max_pages: int = 0) -> str:
    """
    Load and extract text from the first `max_pages` pages of a PDF file using LangChain's PyPDFLoader.

    :param filepath: Path to the PDF file.
    :return: Extracted text as a single string.
    """
    text_chunks = []
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    if max_pages == 0 :
        for page in docs:
            text_chunks.append(page.page_content)
    else :
        for page in docs[:max_pages]:
            text_chunks.append(page.page_content)
    return "\n".join(text_chunks)

def extract_full_pages(path: str, nbpages :int,offset: int = 0):
    loader = PyPDFLoader(path)
    docs = loader.load()[offset:nbpages + offset] 
    return ' '.join(page.page_content for page in docs)
    

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

def ingest_folder(folder_path: str) -> dict[str, dict]:
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
            corpus[fname] = extract_specific_sections(path)
            if corpus[fname]["research_question_sections"] == "Section not found":
                print(f"Warning: nothing found for 'research_question_sections' in {fname}. Extracting full pages instead.")
                corpus[fname]["research_question_sections"] = extract_full_pages(path, 3)
            if corpus[fname]["methodology_sections"] == "Section not found":
                print(f"Warning: nothing found for 'methodology_sections' in {fname}. Extracting full pages instead.")
                corpus[fname]["methodology_sections"] = extract_full_pages(path, 3)
            if corpus[fname]["findings_sections"] == "Section not found":
                print(f"Warning: nothing found for 'findings_sections' in {fname}. Extracting full pages instead.")
                corpus[fname]["findings_sections"] = extract_full_pages(path, 2).join(extract_full_pages(path, 2, -5))
            if corpus[fname]["gaps_sections"] == "Section not found":
                print(f"Warning: nothing found for 'gaps_sections' in {fname}. Extracting full pages instead.")
                corpus[fname]["gaps_sections"] = extract_full_pages(path, 3)
        except Exception as e:
            print(f"Error loading {fname}: {e}")
    
    assert len(corpus) > 0, "No valid PDF files found or loaded."
    
    with open("results/LLM_food.json", "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    return corpus
