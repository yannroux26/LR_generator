from typing import List, Dict
from langfuse import get_client
from langfuse.openai import openai
from .llm_retry import retry_on_rate_limit

langfuse = get_client()

# Prompt template for findings synthesis
PROMPT = '''You are an academic assistant.\
Summarize the key findings of the following paper excerpt.\
List the top 3 most important results or conclusions in concise bullet points.'''

@retry_on_rate_limit
def synthesize_findings(text: str) -> List[str]:
    """
    Calls LLM to extract and synthesize key findings.
    """
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role':'system','content':'You are a findings synthesizer agent.'},
            {'role':'user','content':PROMPT + "\n\n" + text}
        ],
        name="findings_synthesis_request"
    )
    content = response.choices[0].message.content.strip()
    bullets = [line.strip('-•* ') for line in content.splitlines() if line.strip()]
    return bullets


def findings_synthesizer(findings_sections):
    """
    Calls the LLM to synthesize findings from the provided sections of a paper.
    """
    bullets = synthesize_findings(findings_sections)
    return {'findings': bullets}