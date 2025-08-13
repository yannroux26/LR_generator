# rag_pipeline.py — Orchestrates all 11 agents for end-to-end review

import os
from typing import Dict, Any, List
import time
import concurrent.futures

from rag_app.utils.style_applier import apply_writing_style

# Import agents
from .file_loader import ingest_folder
from .metadata_extractor import metadata_extractor
from .research_question import research_question_extractor
from .methodology_summary import methodology_summarizer
from .findings_synthesizer import findings_synthesizer
from .theme_cluster import thematic_synthesizer
from .gap_identifier import gap_identifier
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

def run_rag_litreview(folder_path: str, topic: str=None, writing_style: str=None) -> Dict[str, Any]:
    """
    End-to-end pipeline:
    1. Ingest PDFs → raw text corpus
    2. Metadata, question, method, findings, gaps, citations per paper
    3. Build vector store for retrieval
    4. Cluster themes across all papers
    5. Compose & edit final review
    Returns final edited review plus intermediate data.
    """
    LR_start_time = time.time()
    
    # Dynamically load settings from AppSettings
    try:
        from rag_app.models import AppSettings
        settings = AppSettings.get_solo()
        nbchar = {
            "research_question": settings.research_question_chars,
            "methodology": settings.methodology_chars,
            "findings": settings.findings_chars,
            "gaps": settings.gaps_chars
        }
        max_tokens_compose = settings.max_tokens_compose
        max_tokens_edit = settings.max_tokens_edit
    except Exception as e:
        # fallback to defaults if settings table not ready
        nbchar = {
            "research_question": 5000,
            "methodology": 5000,
            "findings": 5000,
            "gaps": 5000
        }
        max_tokens_compose = 1500
        max_tokens_edit = 1500
    print(f"Using settings: {nbchar}, max_tokens_compose={max_tokens_compose}, max_tokens_edit={max_tokens_edit}")
    corpus = ingest_folder(folder_path, nbchar)
     
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

    # 5. Compose, apply style & edit
    all_data = {"papers": paper_data, "topic": topic}
    all_metadata = [paper["metadata"] for paper in paper_data]
    
    print("\nComposing review")
    status = "COMPLETED"
    try:
        raw_draft = compose_review(all_data, max_tokens=max_tokens_compose)

        if writing_style:
            print("\nApplying writing style")
            LR_styled = apply_writing_style(raw_draft, writing_style, max_tokens=max_tokens_compose)
            
            print("\nEditing review")
            final_review = edit_review(LR_styled, max_tokens=max_tokens_edit, paper_metadata=all_metadata)
        else:
            LR_styled = "no style applied"
            print("\nEditing review")
            final_review = edit_review(raw_draft, max_tokens=max_tokens_edit, paper_metadata=all_metadata)

    except ValueError as e:
        print(f"Error in compose_review: {e}")
        raw_draft = "Error too many papers in input"
        LR_styled = "Error too many papers in input"
        final_review = (
            "Error : The literature review could not be generated, because it would have exceed the Token Per Minute limit (TPM). "
            "Please reduce the number of papers given in input."
        )
        status = "FAILED"

    print(f"Total time needed for the literature review: {time.time() - LR_start_time:.2f} seconds")
    
    # Return full structure
    return {
        "paper_data": paper_data,
        "themes": themes,
        "topic": topic,
        "raw_draft": raw_draft,
        "LR_styled": LR_styled,
        "final_review": final_review,
        "status": status,
    }

