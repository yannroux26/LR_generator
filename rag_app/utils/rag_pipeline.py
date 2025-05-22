# rag_pipeline.py — Orchestrates all 11 agents for end-to-end review

import os
from typing import Dict, Any, List

# Import agents
from .file_loader import ingest_folder
from .metadata_extractor import metadata_extractor
from .research_question import research_question_extractor
from .methodology_summary import methodology_summarizer
from .findings_synthesizer import findings_synthesizer
from .theme_cluster import thematic_synthesizer
from .gap_identifier import gap_identifier
from .citation_mapper import map_citations
from .vector_store import build_vector_store, retrieve_relevant
from .reranker import rerank_excerpts
from .composer import compose_review
from .editor import edit_review

def run_rag_litreview(folder_path: str) -> Dict[str, Any]:
    """
    End-to-end pipeline:
    1. Ingest PDFs → raw text corpus
    2. Metadata, question, method, findings, gaps, citations per paper
    3. Build vector store for retrieval
    4. Cluster themes across all papers
    5. Compose & edit final review
    Returns final edited review plus intermediate data.
    """
    # 1. Ingest
    corpus = ingest_folder(folder_path, max_pages=10)
    
    print("Loaded files :\n", list(corpus.keys()))
    print("200 firsts char of the first document :\n\n" + corpus[list(corpus.keys())[0]][:200])

    # 2. Per-paper agents
    paper_data = []
    for fname, text in corpus.items():
        if text.startswith("ERROR_"):
            continue  # skip load errors
        pdf_path = os.path.join(folder_path, fname)
        
        md = metadata_extractor(pdf_path)
        rq = research_question_extractor(pdf_path)
        meth = methodology_summarizer(pdf_path)
        finds = findings_synthesizer(pdf_path)
        gaps = gap_identifier(pdf_path)
        cites = map_citations(pdf_path)
        
        paper_data.append({
            "filename": fname,
            "metadata": md,
            "research_question": rq.get("research_question", ""),
            "methodology": meth.get("methodology", []),
            "findings": finds.get("findings", []),
            "gaps": gaps.get("gaps", []),
            "references": cites.get("references", [])
        })
    
    # 3. Vector store (for potential ad-hoc retrieval)
    vector_store = build_vector_store(corpus)
    
    # 4. Theme clustering — cluster by paper titles
    titles = [paper["metadata"].get("title", paper["filename"]) for paper in paper_data]
    themes = thematic_synthesizer(titles, n_clusters=min(5, len(titles)))
    # attach theme labels back to papers
    for paper in paper_data:
        paper_title = paper["metadata"].get("title", paper["filename"])
        paper["themes"] = [
            theme for theme, members in themes.items() if paper_title in members
        ]
    
    # 5. Compose & edit
    all_data = {"papers": paper_data}
    raw_draft = compose_review(all_data)
    final_review = edit_review(raw_draft)
    
    # Return full structure
    return {
        "paper_data": paper_data,
        "themes": themes,
        "raw_draft": raw_draft,
        "final_review": final_review
    }
