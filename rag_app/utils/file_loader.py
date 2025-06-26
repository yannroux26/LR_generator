import os
import json
from langchain_community.document_loaders import PyPDFLoader
from Levenshtein import distance
from collections import OrderedDict
from .section_splitter import extract_sections_by_parsing
from .section_splitterv2 import extract_sections_by_format

rq_keywords = ["abstract", "introduction", "summary", "overview"]
metholodology_keywords = ["abstract", "introduction", "summary","method", "methodology", "approach"]
findings_keywords = ["abstract", "summary", "findings", "results", "discussion", "analysis", "interpretation", "conclusion"]
gaps_keywords = [ "introduction","motivation", "literature review","related work", "state of the art","state-of-the-art","future work", "outlook", "limitation"]

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
    matched_sections = OrderedDict()
    
    for keyword in keywords:
        keylist = [title for title in sections.keys() if keyword in title.lower()]
        if keylist:
            # Compute Levenshtein distance between keyword and each key
            min_key = min(keylist, key=lambda k: distance(keyword, k.lower()))
            matched_sections[min_key] = (" ".join(sections[min_key]))[:nbchar]
    return matched_sections


def combine_versions(sectionV1: dict, sectionV2: dict, keywords: list) -> dict:
    combined = dict()
    for keyword in keywords:
        keyv1 = None
        for key in sectionV1:
            if key.lower() in keyword:
                keyv1 = key
                break
        keyv2 = None
        for key in sectionV2:
            if key.lower() in keyword:
                keyv2 = key
                break
            
        if keyv1:
            if keyv2:
                min_key = min(keyv1.lower(), keyv2.lower(), key=lambda k: distance(keyword, k))
                if min_key == keyv2.lower():
                    combined[keyword] = sectionV2[keyv2]
                else:
                    combined[keyword] = sectionV1[keyv1]
            else:
                combined[keyword] = sectionV1[keyv1]
        elif keyv2:
            combined[keyword] = sectionV2[keyv2]

    if not combined or all(not v for v in combined.values()):
        combined = "Section not found"
    return combined


def extract_specific_sections(pdf_path, nbchar: int) -> dict:
    metadatav1, sectionsv1 = extract_sections_by_parsing(pdf_path)
    metadatav2, sectionsv2 = extract_sections_by_format(pdf_path)
    if metadatav1:
        metadata = metadatav1
    elif metadatav2:
        metadata = metadatav2
    else:
        print(f"Warning: no metadata found in {pdf_path}. Extracting full pages instead.")
        metadata = extract_full_pages(pdf_path, 1)[:500]

    rq_sectionsv1 = match_sections_keywords(sectionsv1, rq_keywords, nbchar)
    rq_sectionsv2 = match_sections_keywords(sectionsv2, rq_keywords, nbchar)
    rq_sections = combine_versions(rq_sectionsv1, rq_sectionsv2, rq_keywords)
    if rq_sections == "Section not found":
        print(f"Warning: nothing found for 'research_question_sections' in {pdf_path}. Extracting full pages instead.")
        rq_sections = extract_full_pages(pdf_path, 3)

    methodology_sections = match_sections_keywords(sectionsv1, metholodology_keywords, nbchar)
    methodology_sectionsv2 = match_sections_keywords(sectionsv2, metholodology_keywords, nbchar)
    methodology_sections = combine_versions(methodology_sections, methodology_sectionsv2, metholodology_keywords)
    if methodology_sections == "Section not found":
        print(f"Warning: nothing found for 'methodology_sections' in {pdf_path}. Extracting full pages instead.")
        methodology_sections = extract_full_pages(pdf_path, 3)
    
    findings_sections = match_sections_keywords(sectionsv1, findings_keywords, nbchar)
    findings_sectionsv2 = match_sections_keywords(sectionsv2, findings_keywords, nbchar)
    findings_sections = combine_versions(findings_sections, findings_sectionsv2, findings_keywords)
    if findings_sections == "Section not found":
        print(f"Warning: nothing found for 'findings_sections' in {pdf_path}. Extracting full pages instead.")
        findings_sections = extract_full_pages(pdf_path, 2).join(extract_full_pages(pdf_path, 2, -5))

    gaps_sections = match_sections_keywords(sectionsv1, gaps_keywords, nbchar)
    gaps_sectionsv2 = match_sections_keywords(sectionsv2, gaps_keywords, nbchar)
    gaps_sections = combine_versions(gaps_sections, gaps_sectionsv2, gaps_keywords)
    if gaps_sections == "Section not found":
        print(f"Warning: nothing found for 'gaps_sections' in {pdf_path}. Extracting full pages instead.")
        gaps_sections = extract_full_pages(pdf_path, 3)
    
    return {
        "metadata": metadata,
        "rq_sections": rq_sections,
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
        # try:
        corpus[fname] = extract_specific_sections(path, 5000) 
        for key in corpus[fname]:# convert to JSON format
            if isinstance(corpus[fname][key], dict):
                corpus[fname][key] = json.dumps(corpus[fname][key], ensure_ascii=False, indent=2)
        # except Exception as e:
        #     print(f"Error loading {fname}: {e}")
    
    assert len(corpus) > 0, "No valid PDF files found or loaded."
    
    with open("results/LLM_food.json", "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    return corpus
