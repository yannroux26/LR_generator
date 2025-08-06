from typing import List, Dict
from langfuse import get_client
from langfuse.openai import openai
from .llm_retry import extractor_retry_or_none

langfuse = get_client()
# Prompt template for methodology summarization
PROMPT = '''You are an academic assistant.\
Summarize the methodology section of the following paper excerpt.\
Include study type, data sources, and key techniques.\
Provide 3-4 concise bullet points.'''


@extractor_retry_or_none
def summarize_methodology(text: str) -> List[str]:
    """
    Calls LLM to summarize methodology into bullet points.
    """
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role':'system','content':'You are a methodology summarization agent.'},
            {'role':'user','content':PROMPT + "\n\n" + text}
        ],
        name="methodology_summarization_request"
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