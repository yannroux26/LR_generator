# citation_mapper.py — CitationMappingAgent

import re
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI

openai_client = OpenAI()

# Prompt to extract and normalize citations
CITATION_PROMPT = """
You are a citation mapping agent. Your task is to identify and extract all bibliographic references 
from the following academic paper excerpt. Return the references as a JSON list of dictionaries with the following fields:

- id: Unique reference number (starting from 1)
- full: Full reference string
- authors: List of author names
- title: Title of the paper/book/chapter
- year: Year of publication

Only return valid references. If no references are found, return an empty list.
"""

def extract_references(text: str) -> List[Dict]:
    """
    Calls GPT to extract structured reference data from a string of reference section.
    """
    response = openai_client.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role': 'system', 'content': 'You are a citation extraction agent.'},
            {'role': 'user', 'content': CITATION_PROMPT + "\n\n" + text}
        ]
    )
    result = response.choices[0].message.content
    try:
        import json
        references = json.loads(result)
        return references
    except Exception as e:
        return [{"error": "Failed to parse references", "raw_output": result, "exception": str(e)}]

def extract_reference_section(doc_texts: List[str]) -> str:
    """
    Tries to extract the section containing references or bibliography.
    """
    pattern = re.compile(r'(references|bibliography)', re.IGNORECASE)
    reference_texts = []
    for text in doc_texts[::-1]:  # Search from end
        if pattern.search(text):
            reference_texts.append(text)
            break
    if not reference_texts:
        reference_texts.append(doc_texts[-1])  # fallback: last page
    return "\n".join(reference_texts)

def map_citations(filepath: str) -> Dict:
    """
    Loads a paper and maps its references.
    """
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    doc_texts = [doc.page_content for doc in docs]

    reference_section = extract_reference_section(doc_texts)
    references = extract_references(reference_section)

    return {
        "reference_count": len(references),
        "references": references
    }
