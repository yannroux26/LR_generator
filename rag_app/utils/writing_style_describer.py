from langfuse import get_client
from langfuse.openai import openai
from .llm_retry import retry_on_rate_limit

langfuse = get_client()

describe_prompt = (
    """
You are an expert writing style analyst.
Analyze the following text and provide a concise, objective description of the author's writing style. Focus on tone, structure, vocabulary, sentence complexity, and any notable stylistic features. Do not summarize the content, only describe the style. The text is an extract of a research paper.
"""
)

@retry_on_rate_limit
def describe_writing_style(text: str, max_tokens: int = 512) -> str:
    """
    Calls OpenAI to describe the writing style of the input text.
    Returns only the style description.
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a writing style analysis assistant."},
            {"role": "user", "content": describe_prompt + "\n\n" + text}
        ],
        temperature=0.2,
        max_tokens=max_tokens,
        name="writing_style_description_request"
    )
    return response.choices[0].message.content.strip()
