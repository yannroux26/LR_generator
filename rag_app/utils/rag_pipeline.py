# rag_pipeline.py — Orchestrates all 11 agents for end-to-end review

import os
from typing import Dict, Any, List
import time
import concurrent.futures

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
import json

def process_paper(fname, sections):
    print(f"\nProcessing paper: {fname}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_md = executor.submit(metadata_extractor, sections['metadata'])
        future_rq = executor.submit(research_question_extractor, sections['research_question_sections'])
        future_meth = executor.submit(methodology_summarizer, sections['methodology_sections'])
        future_finds = executor.submit(findings_synthesizer, sections['findings_sections'])
        future_gaps = executor.submit(gap_identifier, sections['gaps_sections'])
        md = future_md.result()
        rq = future_rq.result()
        meth = future_meth.result()
        finds = future_finds.result()
        gaps = future_gaps.result()

    return {
        "filename": fname,
        "metadata": md,
        "research_question": rq.get("research_question", ""),
        "methodology": meth.get("methodology", []),
        "findings": finds.get("findings", []),
        "gaps": gaps.get("gaps", []),
    }

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
    corpus = ingest_folder(folder_path)
    
    # 2. Per-paper agents
    start_time = time.time()
    paper_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_paper, fname, sections)
            for fname, sections in corpus.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            paper_data.append(future.result())
            
    print(f"---Corpus processed in {time.time() - start_time:.2f} seconds---")

    print("\nVectorisation")
    # 3. Vector store (for potential ad-hoc retrieval)
    # vector_store = build_vector_store(corpus)
    
    print("\nTheme clustering")
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
    print("\nComposing review")
    raw_draft = compose_review(all_data)
    print("\nEditing review")
    final_review = edit_review(raw_draft)
    
    # Return full structure
    return {
        "paper_data": paper_data,
        "themes": themes,
        "raw_draft": raw_draft,
        "final_review": final_review
    }

