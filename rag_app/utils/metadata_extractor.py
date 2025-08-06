import os
import json
from typing import Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

from langfuse import get_client
from langfuse.openai import openai
from .llm_retry import extractor_retry_or_none

langfuse = get_client()

# Prompt template
PROMPT = (
    "Extract the metadata: title, authors, journal, year, DOI, and keywords from the following paper text. "
    "Return ONLY a valid JSON object with the keys: title, authors (list), journal, year, doi, keywords (list). "
    "Do not include any explanation, markdown, or text before or after the JSON. "
    "If a value is missing, use null or an empty list."
)


@extractor_retry_or_none
def metadata_extractor(metadata_section) -> Dict:
    """
    call the LLM to extract metadata from the given section of text.
    """
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=[{'role':'system','content':'You are an academic metadata extractor.'},
                  {'role':'user','content':PROMPT + "\n\n" + metadata_section}],
        name="metadata_extraction_request"
    )
    content = response.choices[0].message.content
    try:
        metadata = json.loads(content)
    except json.JSONDecodeError:
        metadata = {'raw_output': content}
    return metadata
