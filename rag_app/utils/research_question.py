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


def research_question_extractor(filepath: str) -> Dict[str,str]:
    """
    Load the first few pages of the PDF and extract its research question.
    """
    from langchain.document_loaders import PyPDFLoader
    loader = PyPDFLoader(filepath)
    docs = loader.load()[0:3]
    text = ' '.join(page.page_content for page in docs)
    question = extract_research_question(text)
    return {'research_question': question}