import os
import json
from langchain_community.document_loaders import PyPDFLoader
from .section_splitterv2 import extract_sections_by_format

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

def extract_full_pages(path: str, nbpages :int,offset: int = 0):
    loader = PyPDFLoader(path)
    docs = loader.load()[offset:nbpages + offset] 
    return ' '.join(page.page_content for page in docs)
    
def match_sections_keywords(sections, keywords, nbchar):
    matched_sections = {}
    for title, content in sections.items():
        title_lower = title.lower()
        if any(kw in title_lower for kw in keywords):
            # We take the first `nbchar` characters of the content to avoid too long sections
            matched_sections[title] = (" ".join(content))[:nbchar]        
    if not matched_sections or all(not v for v in matched_sections.values()):
        matched_sections = "Section not found"
    return matched_sections

def extract_specific_sections(pdf_path, nbchar):
    sections = extract_sections_by_format(pdf_path)
        
    metadata = sections.get("metadata", {})
    
    research_question_keywords = ["abstract", "introduction", "summary", "overview"]
    research_question_sections = match_sections_keywords(sections, research_question_keywords, nbchar)
    
    metholodology_keywords = ["abstract", "introduction", "summary","method", "methodology", "approach"]
    methodology_sections = match_sections_keywords(sections, metholodology_keywords, nbchar)
    
    findings_keywords = ["abstract", "summary", "findings", "results", "discussion", "analysis", "interpretation", "conclusion"]
    findings_sections = match_sections_keywords(sections, findings_keywords, nbchar)

    gaps_keywords = [ "introduction","motivation", "literature review","related work", "state of the art","state-of-the-art","future work", "outlook", "limitation"]
    gaps_sections = match_sections_keywords(sections, gaps_keywords, nbchar)

    return {
        "metadata": metadata,
        "research_question_sections": research_question_sections,
        "methodology_sections": methodology_sections,
        "findings_sections": findings_sections,
        "gaps_sections": gaps_sections
    }
    
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
            corpus[fname] = extract_specific_sections(path, nbchar=5000)
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
            
            for key in corpus[fname]:# convert to JSON format
                if isinstance(corpus[fname][key], dict):
                    corpus[fname][key] = json.dumps(corpus[fname][key], ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error loading {fname}: {e}")
    
    assert len(corpus) > 0, "No valid PDF files found or loaded."
    
    with open("results/LLM_food.json", "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    return corpus
