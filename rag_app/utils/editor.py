from langfuse import get_client
from langfuse.openai import openai
from .llm_retry import retry_on_rate_limit

langfuse = get_client()


def build_editor_prompt(paper_metadata):
    """
    Build the editor prompt, including all paper metadata for reference formatting.
    """
    meta_str = "\n\nPaper metadata for all cited papers (use these to build the reference list):\n"
    for idx, meta in enumerate(paper_metadata, 1):
        meta_lines = [f"  {k}: {v}" for k, v in meta.items()]
        meta_str += f"[{idx}]\n" + "\n".join(meta_lines) + "\n"
    return f"""
You are a scholarly editor.
Please refine the following literature review draft for academic clarity, coherence, and readability. Also:

- Format all in‑text citations and the reference list in IEEE style (numbered [1], [2], …).
- Ensure all citations of papers contain a DOI.
- Ensure section headings remain intact.
- Provide the formatted reference list at the end under the heading “References”.

{meta_str}
"""

@retry_on_rate_limit
def edit_review(draft_text: str, max_tokens: int, paper_metadata: list) -> str:
    """
    Calls LLM to edit the draft into final polished form with IEEE citations, using all paper metadata for accurate references.
    :param draft_text: The raw composed literature review.
    :param max_tokens: Max tokens for the LLM response.
    :param paper_metadata: List of dicts, one per paper, with all metadata fields.
    :return: Polished review with IEEE-style citations.
    """
    prompt = build_editor_prompt(paper_metadata) + "\n\n" + draft_text
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a scholarly editor assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=max_tokens,
        name="review_editing_request"
    )
    return response.choices[0].message.content.strip()
