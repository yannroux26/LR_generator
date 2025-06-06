# rag_app/utils/editor.py   # EditorAgent

from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI()

# Prompt template for editing and IEEE formatting
EDITOR_PROMPT = """
You are a scholarly editor.
Please refine the following literature review draft for academic clarity, coherence, and readability. Also:

- Format all in‑text citations and the reference list in IEEE style (numbered [1], [2], …).
- Ensure all citations of papers contain a doi.
- Ensure section headings remain intact.
- Provide the formatted reference list at the end under the heading “References”.
"""

def edit_review(draft_text: str) -> str:
    """
    Calls LLM to edit the draft into final polished form with IEEE citations.
    
    :param draft_text: The raw composed literature review.
    :return: Polished review with IEEE-style citations.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a scholarly editor assistant."},
            {"role": "user", "content": EDITOR_PROMPT + "\n\n" + draft_text}
        ],
        temperature=0.3,
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()
