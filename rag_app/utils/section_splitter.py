from langchain.document_loaders import PyPDFLoader
import re
import sys

def extract_sections_from_pdf(path):
    loader = PyPDFLoader(path)
    pages = loader.load()
    full_text = "\n".join([page.page_content for page in pages])
    
    # Titre & auteurs depuis la 1ère page
    first_page = pages[0].page_content
    lines = first_page.strip().split('\n')
    title = lines[0].strip()
    authors = lines[1].strip()
    
    print("\nPremières 5 lignes du PDF :")
    for line in lines[:5]:
        print(line)

    # Regex sur sections
    section_headers = [
        "abstract", "summary",
        "keywords?", "key terms", "index terms",
        "introduction", "background", "overview",
        "related works?", "previous works?", "prior work", "literature review", "state of the art",
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
    pattern = r"\n\s*(%s)\s*\n" % "|".join(section_headers)
    splits = re.split(pattern, full_text, flags=re.IGNORECASE)

    sections = {}
    for i in range(1, len(splits), 2):
        section = splits[i].strip().lower()
        content = splits[i + 1].strip()
        sections[section] = content

    return {
        "title": title,
        "authors": authors,
        **sections
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python section_splitter.py <pdf_path>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    result = extract_sections_from_pdf(pdf_path)

    print("\nSections extraites de l'article :")
    for key, value in result.items():
        print(f"{key}:\n {value[:200]}{'...' if len(value) > 200 else ''}\n")