#!/usr/bin/env python3
"""Build a small FTS5 index from papers.yaml and project research docs."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "papers.yaml"
DOC_ROOT = ROOT / "docs" / "ai-anime-production"
OUT = ROOT / "rag" / "data" / "rag2.db"
CHUNK_SIZE = 1600
OVERLAP = 180

def split_text(text: str):
    text = text.strip()
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        if end < len(text):
            cut = text.rfind("\n", start + CHUNK_SIZE // 2, end)
            if cut > start:
                end = cut
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end >= len(text):
            break
        start = max(start + 1, end - OVERLAP)

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    conn = sqlite3.connect(OUT)
    conn.executescript("""
      PRAGMA journal_mode=DELETE;
      CREATE TABLE documents(
        id TEXT PRIMARY KEY, title TEXT NOT NULL, source_uri TEXT NOT NULL,
        source_type TEXT NOT NULL, metadata_json TEXT NOT NULL
      );
      CREATE TABLE chunks(
        id INTEGER PRIMARY KEY, document_id TEXT NOT NULL, chunk_index INTEGER NOT NULL,
        text TEXT NOT NULL, UNIQUE(document_id, chunk_index),
        FOREIGN KEY(document_id) REFERENCES documents(id)
      );
      CREATE VIRTUAL TABLE chunks_fts USING fts5(
        title, text, content='chunks', content_rowid='id', tokenize='unicode61'
      );
      CREATE TRIGGER chunks_ai AFTER INSERT ON chunks BEGIN
        INSERT INTO chunks_fts(rowid,title,text)
        SELECT new.id, documents.title, new.text FROM documents WHERE documents.id=new.document_id;
      END;
      CREATE TABLE build_info(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    """)
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    for paper in manifest.get("papers", []):
        doc_id = "paper:" + paper["id"]
        conn.execute("INSERT INTO documents VALUES(?,?,?,?,?)", (
            doc_id, paper["title"], paper.get("url", ""), "paper_metadata",
            json.dumps(paper, ensure_ascii=False, sort_keys=True)))
        text = "\n".join([
            paper["title"], "Topics: " + ", ".join(paper.get("topics", [])),
            "Research use: " + paper.get("research_use", ""),
            "Verification: " + paper.get("verification", ""),
            "URL: " + paper.get("url", "")])
        for i, chunk in enumerate(split_text(text)):
            conn.execute("INSERT INTO chunks(document_id,chunk_index,text) VALUES(?,?,?)", (doc_id,i,chunk))
    for path in sorted(DOC_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".tex", ".mmd", ".puml"}:
            continue
        if path.name == "network.yaml" and "nwman" in path.parts:
            pass
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(ROOT).as_posix()
        doc_id = "doc:" + rel
        conn.execute("INSERT INTO documents VALUES(?,?,?,?,?)", (
            doc_id, path.stem.replace("-", " "), rel, "project_document",
            json.dumps({"path": rel, "suffix": path.suffix}, ensure_ascii=False)))
        for i, chunk in enumerate(split_text(content)):
            conn.execute("INSERT INTO chunks(document_id,chunk_index,text) VALUES(?,?,?)", (doc_id,i,chunk))
    info = {
        "schema_version": "1.0",
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "manifest": "papers.yaml",
        "scope": "paper metadata and project documents; not full paper PDF text",
    }
    conn.executemany("INSERT INTO build_info VALUES(?,?)", info.items())
    conn.commit()
    conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
    conn.commit()
    docs = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
    chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    conn.close()
    print(f"Built {OUT}: documents={docs}, chunks={chunks}")

if __name__ == "__main__":
    main()
