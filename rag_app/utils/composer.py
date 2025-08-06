from typing import Dict, Any
from langfuse import get_client
from langfuse.openai import openai
from .llm_retry import retry_on_rate_limit

langfuse = get_client()

# Prompt template to compose the review
COMPOSER_PROMPT = """
You are a senior researcher tasked with writing a literature review. Given the following structured data for multiple papers, draft a comprehensive review.
If a topic is provided, the review should focus on that topic. If no topic is provided, synthesize the literature more generally.
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
  ],
  "topic": "..." (Can be None)
}

Structure the output with headings:
1. Introduction
2. Thematic Synthesis
3. Research Gaps
4. Conclusion

Write in academic style, cite each paper by its title in parentheses where appropriate.
"""

@retry_on_rate_limit
def compose_review(all_paper_data: Dict[str, Any], max_tokens: int) -> str:
    """
    all_paper_data should be a dict:
    {
      "papers": [
         { ... agent outputs per paper ... },
         ...
      ],
      "topic": "Optional topic for the review"
    }
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a literature review composer."},
            {"role": "user", "content": COMPOSER_PROMPT + "\n\n" + str(all_paper_data)}
        ],
        temperature=0.7,
        max_tokens=max_tokens,
        name="review_composition_request"
    )
    return response.choices[0].message.content.strip()
