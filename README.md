# LR_generator

## Project Overview
- This project is an end-to-end pipeline for automated literature review generation using agentic AI.
- Major components are organized as Django apps and Python modules under `rag_app/utils/`.
- the pipeline follow this order :
    1. The user provide the path to a folder of documents (via the interface or command line)
    2. Loading PDF
    3. Metadata, question, method, findings and gaps summarization per paper
    4. Cluster themes across all papers
    5. Composition of a first draft
    6. Edit final review
    7. Display the final edited review plus intermediate data.
- The pipeline orchestrates multiple agents: loader, metadata extraction, research question extraction, methodology summarization, findings synthesis, theme clustering, gap identification, composition, and editing.

## User Instructions

### Initial Setup
These steps are only necessary when cloning the project for the first time or performing a fresh installation.
- **Clone the repository:**
```bash
git clone https://github.com/ton-nom-utilisateur/ton-projet.git
cd your-project
```
- **Create an environment:**
With conda 
```bash
conda create --name <environment-name>
```
Without conda :
```bash
python -m venv <environment-name>
```

- **Install dependencies:**
```bash
pip install -r requirements.txt
```
- **Configure environment variables**:
  Set OpenAI and Langfuse keys in the `.env` file, see `env_file_template`.

- **Set up the database:**
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### Regular use 
- **Activate your environment:**
With conda 
```bash
conda activate <environment-name>
```
Without conda (on Windows):
```bash
<nom_de_l'environnement>\Scripts\activate
```

- **Launch the server:**
```bash
python manage.py runserv
```
- **Open the interface**
Click on the links give, in the in the command shell as :
`Starting development server at http://127.0.0.1:8000/`

- **(Optionnal) Configure the parameters**
- **Generate a literature review :** 
  Provide the path of the folder containing the pdf files. Then press `Enter` or click on `Generate`
Have fun :D

## Developer instructions

- **Run the pipeline from command line:**
  ```bash
  python main.py path/to/folder/ # or use Django views for web interface
  ```

### Key Architectural Patterns
- **Agent Pattern:** Each major NLP/LLM task is encapsulated as a function in its own file (e.g., `metadata_extractor.py`, `methodology_summary.py`). All agent calls are orchestrated in `rag_pipeline.py`.
- **Parallel Processing:** Per-paper agent calls are parallelized using `concurrent.futures.ThreadPoolExecutor` for efficiency (see in `rag_pipeline.py`).
- **Langfuse Integration:** LLM calls are traced and tagged using Langfuse for observability and evaluation. Tags are set via the Langfuse SDK, not as OpenAI parameters.
- **Section Extraction:** PDF parsing and section splitting are handled by dedicated utilities (e.g., `section_splitter.py`, `file_loader.py`) to optimize the length of text given to LLMs.

### Project-Specific Conventions
- **LLM calls for evaluation must be tagged** (e.g., `tags=["metadata"]`) using Langfuse's trace/generation API, to be easy to track with langfuse.
- **Retry Logic:** All LLM calls are wrapped with a custom `retry_on_rate_limit` decorator (see `LLM_retry.py`) to handle OpenAI rate limits error.

### Key Files & Directories
- `rag_app/utils/rag_pipeline.py`: Main pipeline orchestrator, parallelization logic.
- `rag_app/utils/metadata_extractor.py`, `methodology_summary.py`, etc.: Agent implementations.
- `rag_app/utils/file_loader.py`, PDF and section parsing orchestrator.
- `.env` or environment: Store API keys for OpenAI and Langfuse.
- `rag_app/utils/LLM_retry.py`: Retry decorator for OpenAI rate limits.

### Integration Points
- **OpenAI:** All LLM calls use the OpenAI API via the Langfuse-wrapped client.
- **Langfuse:** Used for tracing, tagging, and evaluating LLM generations. Tags are critical for filtering in the Langfuse UI.
- **Django:** Used for web interface and database management (see `manage.py`, `models.py`).

### Example: Adding a New Agent
1. Create a new file in `rag_app/utils/` (e.g., `my_agent.py`).
2. Implement the agent function and decorate LLM-call with `@retry_on_rate_limit`.
3. Integrate the agent call in `rag_pipeline.py`.
4. If the agent uses LLM, wrap the call with Langfuse tracing and tagging.

---
