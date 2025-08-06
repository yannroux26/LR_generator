from langchain_community.document_loaders import PyPDFLoader
import re
import sys

def extract_sections_by_parsing(path):
    loader = PyPDFLoader(path)
    pages = loader.load()
    full_text = "\n".join([page.page_content for page in pages])

    # Regex sur sections
    section_headers = [
        "abstract", "summary",
        "keywords?", "key terms", "index terms",
        "introduction", "background", "overview",
        "related works?", "previous works?", "recent work", "prior work", "literature review", "state of the art","state-of-the-art",
        "methods?", "methodology", "approach", "materials and methods",
        "experiment", "experimental setup", "implementation details", "experimental details",
        "results?", "findings", "evaluation results",
        "discussion", "analysis", "interpretation",
        "conclusion", "concluding remarks?", "summary and conclusion",
        "future work", "outlook", "limitations?","limitations and future work",
        "acknowledgment", "thanks",
        "references", "bibliography", "works cited",
        "appendix", "supplementary materials"
    ]
    
    pattern = r"\n\s*(\d.\.?)*\s*(%s)\s*:?\s*\n" % "|".join(section_headers)
    splits = re.split(pattern, full_text, flags=re.IGNORECASE)

    # Cleaning up splits
    splits = [s for s in splits if s is not None]
    splits = [s for s in splits if not re.fullmatch(r"(\d\.?)+", s.strip())]
    
    sections = {}
    metadata = ""
    # Cherche la position de "abstract" dans splits
    abstract_idx = None
    for i in range(1, len(splits), 2):
        section = splits[i].strip().lower()
        content = splits[i + 1].strip()
        sections[section] = content
        if section == "abstract" and abstract_idx is None:
            abstract_idx = i

    if abstract_idx is not None:
        metadata = "".join([splits[j].strip() for j in range(0, abstract_idx)]).strip()
    return metadata, sections

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python section_splitter.py <pdf_path>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    metadata, result = extract_sections_by_parsing(pdf_path)

    print("\n--- METADATA ---\n")
    print(metadata[:500])  # Affiche les 500 premiers caractères du metadata

    print("\nSections extraites de l'article :")
    for key, value in result.items():
        print("=="* 50)
        print(f"{key}:\n")
        print("--" * 50)
        print(value[:1000])