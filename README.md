# LR_generator

## Project Overview
- This project is an end-to-end pipeline for automated literature review generation using agentic AI.
- Major components are organized as Django apps and Python modules under `rag_app/utils/`.
- The pipeline orchestrates multiple agents: metadata extraction, research question extraction, methodology summarization, findings synthesis, theme clustering, gap identification, citation mapping, vector store building, reranking, review composition, and editing.

## Key Architectural Patterns
- **Agent Pattern:** Each major NLP/LLM task is encapsulated as a function in its own file (e.g., `metadata_extractor.py`, `methodology_summary.py`). All agent calls are orchestrated in `rag_pipeline.py`.
- **Parallel Processing:** Per-paper agent calls are parallelized using `concurrent.futures.ThreadPoolExecutor` for efficiency (see `run_rag_litreview` in `rag_pipeline.py`).
- **Langfuse Integration:** LLM calls are traced and tagged using Langfuse for observability and evaluation. Tags are set via the Langfuse SDK, not as OpenAI parameters.
- **Section Extraction:** PDF parsing and section splitting are handled by dedicated utilities (e.g., `section_splitter.py`, `file_loader.py`) to optimize the length of text given to LLMs.

## Developer Workflows
- **Run the pipeline:**
  ```bash
  python main.py path/to/folder/ # or use Django views for web interface
  ```
- **Migrations:**
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
- **Environment variables:**
  - Set OpenAI and Langfuse keys in the `.env` file, see `env_file_template`.

## Project-Specific Conventions
- **LLM calls for evaluation must be tagged** (e.g., `tags=["metadata"]`) using Langfuse's trace/generation API, to be easy to track with langfuse.
- **Retry Logic:** All LLM calls are wrapped with a custom `retry_on_rate_limit` decorator (see `LLM_retry.py`) to handle OpenAI rate limits error.

## Key Files & Directories
- `rag_app/utils/rag_pipeline.py`: Main pipeline orchestrator, parallelization logic.
- `rag_app/utils/metadata_extractor.py`, `methodology_summary.py`, etc.: Agent implementations.
- `rag_app/utils/file_loader.py`, PDF and section parsing orchestrator.
- `.env` or environment: Store API keys for OpenAI and Langfuse.
- `rag_app/utils/LLM_retry.py`: Retry decorator for OpenAI rate limits.

## Integration Points
- **OpenAI:** All LLM calls use the OpenAI API via the Langfuse-wrapped client.
- **Langfuse:** Used for tracing, tagging, and evaluating LLM generations. Tags are critical for filtering in the Langfuse UI.
- **Django:** Used for web interface and database management (see `manage.py`, `models.py`).

## Example: Adding a New Agent
1. Create a new file in `rag_app/utils/` (e.g., `my_agent.py`).
2. Implement the agent function and decorate LLM-call with `@retry_on_rate_limit`.
3. Integrate the agent call in `rag_pipeline.py`.
4. If the agent uses LLM, wrap the call with Langfuse tracing and tagging.

---
