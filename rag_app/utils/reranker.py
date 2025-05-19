# reranker.py   # RelevanceRerankerAgent

from typing import List, Tuple
from openai import OpenAI
from langchain.docstore.document import Document

openai_client = OpenAI()

# Prompt template to score relevance
SCORE_PROMPT_TEMPLATE = """You are an expert academic reviewer.
Given the query and a document excerpt, rate how relevant the excerpt is to answering the query on a scale from 1 (irrelevant) to 5 (highly relevant).
Respond with just a number between 1 and 5.

Query: {query}

Excerpt:
\"\"\"
{excerpt}
\"\"\""""

def score_relevance(query: str, excerpt: str) -> int:
    """Call the LLM to score the relevance of one excerpt."""
    prompt = SCORE_PROMPT_TEMPLATE.format(query=query, excerpt=excerpt)
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        score = int(response.choices[0].message.content.strip())
    except ValueError:
        score = 1
    return score

def rerank_excerpts(
    query: str, 
    candidates: List[Tuple[str, str]]
) -> List[Tuple[str, str]]:
    """
    Rerank candidate excerpts based on LLM relevance scores.
    :param query: The user or agent query string.
    :param candidates: List of (source_doc_id, excerpt_text).
    :return: Candidates sorted by descending relevance.
    """
    scored: List[Tuple[int, str, str]] = []
    for doc_id, excerpt in candidates:
        score = score_relevance(query, excerpt)
        scored.append((score, doc_id, excerpt))

    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])
    # Return top excerpts (dropping score)
    return [(doc_id, excerpt) for score, doc_id, excerpt in scored]
