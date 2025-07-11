from typing import Dict, Any
from langfuse import get_client
from langfuse.openai import openai

langfuse = get_client()

# Prompt template to compose the review
COMPOSER_PROMPT = """
You are a senior researcher tasked with writing a literature review. Given the following structured data for multiple papers, draft a comprehensive review.

Data format (JSON):
{
  "papers": [
    {
      "filename": "...pdf",
      "metadata": {title, authors, journal, year, doi, keywords},
      "research_question": "...",
      "methodology": ["...","..."],
      "findings": ["...","..."],
      "themes": ["...","..."],       # from thematic clustering
      "gaps": ["...","..."],
    },
    ...
  ]
}

Structure the output with headings:
1. Introduction
2. Thematic Synthesis
3. Research Gaps
4. Conclusion

Write in academic style, cite each paper by its title in parentheses where appropriate.
"""

def compose_review(all_paper_data: Dict[str, Any]) -> str:
    """
    all_paper_data should be a dict:
    {
      "papers": [
         { ... agent outputs per paper ... },
         ...
      ]
    }
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a literature review composer."},
            {"role": "user", "content": COMPOSER_PROMPT + "\n\n" + str(all_paper_data)}
        ],
        temperature=0.7,
        max_tokens=1500,
        name="review_composition_request"
    )
    return response.choices[0].message.content.strip()
