import json
from typing import Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from openai import OpenAI

# Initialize OpenAI client (ensure API key is set in environment)
openai_client = OpenAI()

# Prompt template
PROMPT = '''Extract the metadata: title, authors, journal, year, DOI, and keywords from the following paper text. Return a JSON object with keys: title, authors (list), journal, year, doi, keywords (list).'''


def extract_metadata_from_text(text: str) -> Dict:
    """
    Uses LLM to extract standardized metadata from a paper's text.
    """
    response = openai_client.chat.completions.create(
        model='gpt-4',
        messages=[{'role':'system','content':'You are an academic metadata extractor.'},
                  {'role':'user','content':PROMPT + "\n\n" + text}]
    )
    content = response.choices[0].message.content
    try:
        metadata = json.loads(content)
    except json.JSONDecodeError:
        # fallback: wrap raw content
        metadata = {'raw_output': content}
    return metadata


def metadata_extractor(filepath: str) -> Dict:
    """
    Load PDF, extract text, then extract metadata.
    """
    # use 2 pages for metadata extraction context
    loader = PyPDFLoader(filepath)
    docs = loader.load()[0:2]
    text = ' '.join(page.page_content for page in docs)
    return extract_metadata_from_text(text)