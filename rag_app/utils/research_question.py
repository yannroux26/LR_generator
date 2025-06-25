from typing import Dict
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI()

# Prompt template to extract research question or hypothesis
PROMPT = '''You are an expert researcher.\
Extract the main research question or hypothesis from the following academic paper excerpt.\
Respond in one sentence.'''


def extract_research_question(text: str) -> str:
    """
    Calls LLM to extract the core research question or hypothesis.
    """
    response = openai_client.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role':'system','content':'You are a research question extraction agent.'},
            {'role':'user','content':PROMPT + "\n\n" + text}
        ]
    )
    return response.choices[0].message.content.strip()


def research_question_extractor(research_question_sections) -> Dict[str,str]:
    """
    call the LLM to extract the research question from the given sections of text.
    """
    question = extract_research_question(research_question_sections)
    return {'research_question': question}