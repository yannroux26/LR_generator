from typing import List, Dict
from langfuse import get_client
from langfuse.openai import openai

langfuse = get_client()

# Prompt template to identify research gaps
PROMPT = '''You are an expert academic reviewer.\
Identify 2-3 research gaps based on the abstract and methodology of the following paper excerpt.\
Output each gap as a concise bullet point.'''  

def identify_gaps(text: str) -> List[str]:
    """
    Calls LLM to extract research gaps.
    """
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role':'system','content':'You are a gap identification agent.'},
            {'role':'user','content':PROMPT + '\n\n' + text}
        ],
        name="gap_identification_request"
    )
    content = response.choices[0].message.content.strip()
    bullets = [line.strip('-•* ') for line in content.splitlines() if line.strip()]
    return bullets

def gap_identifier(gaps_sections: str):
    """
    Calls the LLM to identify research gaps from the provided sections of a paper.
    """
    gaps = identify_gaps(gaps_sections)
    return {'gaps': gaps}
