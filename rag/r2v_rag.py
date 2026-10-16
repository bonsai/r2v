#!/usr/bin/env python3
"""Local full-text RAG for the three R2V papers in papers.yml."""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

import fitz
import yaml

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "papers.yml"
DATA = ROOT / "data"
DEFAULT_DB = DATA / "r2v_rag.sqlite3"
CHUNK_CHARS = 1400
OVERLAP_CHARS = 220


def load_papers() -> list[dict]:
    with MANIFEST.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)["papers"]


def db_path() -> Path:
    return Path(os.environ.get("R2V_RAG_DB", str(DEFAULT_DB))).expanduser()


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            paper_id TEXT NOT NULL,
            title TEXT NOT NULL,
            arxiv_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            page INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            UNIQUE(paper_id, page, chunk_index)
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            title, text, content='chunks', content_rowid='id',
            tokenize='unicode61'
        )
    """)
    conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
          INSERT INTO chunks_fts(rowid, title, text) VALUES (new.id, new.title, new.text);
        END;
        CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
          INSERT INTO chunks_fts(chunks_fts, rowid, title, text)
          VALUES('delete', old.id, old.title, old.text);
        END;
        CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
          INSERT INTO chunks_fts(chunks_fts, rowid, title, text)
          VALUES('delete', old.id, old.title, old.text);
          INSERT INTO chunks_fts(rowid, title, text) VALUES (new.id, new.title, new.text);
        END;
    """)
    conn.commit()
    return conn


def download_pdf(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": "bonsai-r2v-local-research/0.1"}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as out:
            out.write(response.read())
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not download {url}: {exc}") from exc


def split_text(text: str) -> Iterable[str]:
    # Preserve paragraph boundaries where possible, while ensuring long paragraphs fit.
    text = re.sub(r"[ \t]+", " ", text).strip()
    if not text:
        return
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_CHARS)
        if end < len(text):
            boundary = text.rfind("\n", start + CHUNK_CHARS // 2, end)
            if boundary > start:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end >= len(text):
            break
        start = max(start + 1, end - OVERLAP_CHARS)


def ingest(download: bool) -> None:
    papers = load_papers()
    conn = connect()
    for paper in papers:
        pdf_path = ROOT / paper["local_pdf"]
        if not pdf_path.exists() and download:
            print(f"Downloading {paper['arxiv_id']} ...")
            download_pdf(paper["pdf_url"], pdf_path)
        if not pdf_path.exists():
            print(f"SKIP {paper['arxiv_id']}: PDF not found. Use ingest --download.", file=sys.stderr)
            continue
        print(f"Indexing {paper['title']} ...")
        doc = fitz.open(pdf_path)
        conn.execute("DELETE FROM chunks WHERE paper_id = ?", (paper["id"],))
        count = 0
        for page_idx, page in enumerate(doc, start=1):
            page_text = page.get_text("text", sort=True)
            for chunk_idx, chunk in enumerate(split_text(page_text)):
                conn.execute(
                    """INSERT INTO chunks
                       (paper_id,title,arxiv_id,source_url,page,chunk_index,text)
                       VALUES(?,?,?,?,?,?,?)""",
                    (paper["id"], paper["title"], paper["arxiv_id"],
                     paper["url"], page_idx, chunk_idx, chunk),
                )
                count += 1
        conn.commit()
        doc.close()
        print(f"  indexed {count} chunks")
    conn.close()
    print(f"Index: {db_path()}")


def search(query: str, limit: int = 6) -> list[sqlite3.Row]:
    conn = connect()
    # FTS5 syntax is not user-friendly; quote each word and OR them to avoid
    # malformed MATCH expressions from punctuation in natural-language questions.
    terms = re.findall(r"[\w-]+", query, flags=re.UNICODE)
    terms = [t for t in terms if len(t) > 1][:20]
    if not terms:
        conn.close()
        return []
    match_query = " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)
    rows = conn.execute("""
        SELECT c.*, bm25(chunks_fts, 2.0, 1.0) AS score
        FROM chunks_fts
        JOIN chunks c ON c.id = chunks_fts.rowid
        WHERE chunks_fts MATCH ?
        ORDER BY score
        LIMIT ?
    """, (match_query, limit)).fetchall()
    conn.close()
    return rows


def generate_answer(question: str, rows: list[sqlite3.Row]) -> str:
    base_url = os.environ.get("R2V_RAG_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("R2V_RAG_API_KEY", "")
    model = os.environ.get("R2V_RAG_MODEL", "")
    if not (base_url and model):
        raise RuntimeError("Set R2V_RAG_BASE_URL and R2V_RAG_MODEL to enable generation.")
    evidence = "\n\n".join(
        f"[{i}] {r['title']} (arXiv:{r['arxiv_id']}, p.{r['page']})\n{r['text']}"
        for i, r in enumerate(rows, start=1)
    )
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content":
             "You are a careful research assistant. Answer only from the supplied evidence. "
             "If evidence is insufficient, say so. Cite claims with [paper title, p. N]. "
             "Distinguish paper claims from your own comparison; do not invent metrics."},
            {"role": "user", "content": f"Question: {question}\n\nEvidence:\n{evidence}"}
        ],
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {api_key}"} if api_key else {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Generation request failed: {exc}") from exc


def ask(question: str, limit: int, generate: bool) -> None:
    rows = search(question, limit)
    if not rows:
        print("No matching chunks. Run: python rag/r2v_rag.py ingest --download")
        return
    if generate:
        print(generate_answer(question, rows))
        print("\n--- Retrieved sources ---")
    for i, row in enumerate(rows, start=1):
        print(f"\n[{i}] {row['title']} | arXiv:{row['arxiv_id']} | p.{row['page']}")
        print(row["source_url"])
        print(row["text"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    ingest_parser = sub.add_parser("ingest", help="extract full text and build the index")
    ingest_parser.add_argument("--download", action="store_true",
                               help="download missing PDFs from arXiv first")
    ask_parser = sub.add_parser("ask", help="retrieve evidence and optionally generate an answer")
    ask_parser.add_argument("question")
    ask_parser.add_argument("--limit", type=int, default=6)
    ask_parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    if args.command == "ingest":
        ingest(args.download)
    elif args.command == "ask":
        ask(args.question, max(1, min(args.limit, 20)), args.generate)


if __name__ == "__main__":
    main()
