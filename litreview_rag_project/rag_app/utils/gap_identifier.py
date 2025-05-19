# gap_identifier.py    # GapIdentifierAgent

from typing import List, Dict
from openai import OpenAI
from langchain.document_loaders import PyPDFLoader

# Initialize OpenAI client
openai_client = OpenAI()

# Prompt template to identify research gaps
PROMPT = '''You are an expert academic reviewer.\
Identify 2-3 research gaps based on the abstract and methodology of the following paper excerpt.\
Output each gap as a concise bullet point.'''  

def identify_gaps(text: str) -> List[str]:
    """
    Calls LLM to extract research gaps.
    """
    response = openai_client.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role':'system','content':'You are a gap identification agent.'},
            {'role':'user','content':PROMPT + '\n\n' + text}
        ]
    )
    content = response.choices[0].message.content.strip()
    bullets = [line.strip('-•* ') for line in content.splitlines() if line.strip()]
    return bullets

def gap_identifier(filepath: str) -> Dict[str, List[str]]:
    """
    Load abstract and methodology pages and identify gaps.
    """
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    text = ' '.join([docs[0].page_content] + [p.page_content for p in docs[1:4]])
    gaps = identify_gaps(text)
    return {'gaps': gaps}
