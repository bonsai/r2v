# R2V Paper RAG

A local-first RAG pipeline for the full text of the three papers tracked in this repository.

## What it does

- Downloads the source PDFs from arXiv on demand.
- Extracts page-aware text and stores chunks plus source/page metadata in SQLite FTS5.
- Retrieves relevant chunks with lexical full-text search.
- Optionally sends the retrieved evidence to an OpenAI-compatible chat-completions endpoint to draft an answer with paper/page citations.
- Keeps PDFs, extracted text, and the index local; generated data is git-ignored.

## Papers

See [papers.yml](papers.yml). The source records are the arXiv pages for Saber, RefAlign, and OmniVBench.

## Quick start

From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r rag/requirements.txt

# Download PDFs and build the local full-text index
python rag/r2v_rag.py ingest --download

# Retrieve evidence without an LLM
python rag/r2v_rag.py ask "How does each paper preserve reference identity?"

# Optional: answer using an OpenAI-compatible endpoint
# Set these environment variables for your chosen provider:
# R2V_RAG_BASE_URL, R2V_RAG_API_KEY, R2V_RAG_MODEL
python rag/r2v_rag.py ask "Compare the evaluation methods" --generate
```

If your provider uses a different API shape, use retrieval-only mode; the index does not depend on an LLM provider.

## Environment variables

- `R2V_RAG_BASE_URL`: API base URL, e.g. `https://api.openai.com/v1` (must support `/chat/completions`).
- `R2V_RAG_API_KEY`: API key. Do not commit it.
- `R2V_RAG_MODEL`: model identifier supplied by the provider.
- `R2V_RAG_DB`: optional SQLite path; defaults to `rag/data/r2v_rag.sqlite3`.

## Data and licensing

PDFs are downloaded only when you explicitly run `ingest --download`. They are not committed to Git. Check each paper's current arXiv license and any publisher terms before redistributing source files or extracted full text. The index is intended for local research; keep the source URL and page number attached to every retrieved chunk.

## Current limitations

- Retrieval uses SQLite FTS5 keyword search, not vector embeddings. It is a small, reproducible baseline that works on CPU and does not require a hosted vector database.
- PDF extraction quality depends on the paper's layout. Tables, equations, and multi-column text may need manual verification against the original PDF.
- Generated answers are constrained to retrieved excerpts, but citations should still be checked against the source PDF.
