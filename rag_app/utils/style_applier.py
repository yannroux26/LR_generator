from langfuse import get_client
from langfuse.openai import openai
from .llm_retry import retry_on_rate_limit

langfuse = get_client()

def build_style_applier_prompt(writing_style: str) -> str:
    """
    Build the prompt to instruct the LLM to rewrite a literature review in the provided writing style.
    """
    return f"""
You are a scholarly writing assistant.
Rewrite the following literature review so that it matches the provided writing style as closely as possible.

---
Writing Style Example:
{writing_style}
---

Maintain the academic tone, structure, and content of the review, but adapt the phrasing, sentence structure, and word choice to reflect the given writing style. Do not add or remove information.
"""

@retry_on_rate_limit
def apply_writing_style(lit_review: str, writing_style: str, max_tokens: int = 2048) -> str:
    """
    Calls LLM to rewrite the literature review using the provided writing style.
    :param lit_review: The original literature review text.
    :param writing_style: The writing style sample to emulate.
    :param max_tokens: Max tokens for the LLM response.
    :return: The rewritten literature review in the target style.
    """
    prompt = build_style_applier_prompt(writing_style) + "\n\n" + lit_review
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a scholarly writing style applier."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=max_tokens,
        name="style_applier_request"
    )
    return response.choices[0].message.content.strip()
