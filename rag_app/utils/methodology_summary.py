from typing import List, Dict
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader

# Initialize OpenAI client
openai_client = OpenAI()

# Prompt template for methodology summarization
PROMPT = '''You are an academic assistant.\
Summarize the methodology section of the following paper excerpt.\
Include study type, data sources, and key techniques.\
Provide 3-4 concise bullet points.'''


def summarize_methodology(text: str) -> List[str]:
    """
    Calls LLM to summarize methodology into bullet points.
    """
    response = openai_client.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role':'system','content':'You are a methodology summarization agent.'},
            {'role':'user','content':PROMPT + "\n\n" + text}
        ]
    )
    content = response.choices[0].message.content.strip()
    bullets = [line.strip('-•* ') for line in content.splitlines() if line.strip()]
    return bullets


def methodology_summarizer(methodology_sections) -> Dict[str, List[str]]:
    """
    Calls the LLM to summarize the methodology sections of a paper.
    """
    bullets = summarize_methodology(methodology_sections)
    return {'methodology': bullets}