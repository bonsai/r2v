# R2V Research Notes

Research notes for Reference-to-Video (R2V) generation: generating a video that follows a text prompt while preserving or controlling information from reference images.

> Scope note: this repository began as R2V research notes and now also contains a scoped research proposal for a structured AI anime production system. The TPS/Software Factory integration and all claimed benefits remain hypotheses until experimentally validated.

## Research questions

- How can a model preserve the identity of a person or object from reference images across generated frames?
- How can it follow text instructions without copying reference pixels into the video?
- How should multiple reference images and different factors (content, motion, style, structure, narrative) be controlled independently?
- What data and evaluation protocols are needed to measure reference fidelity and instruction following?
- Which controllable process variable delivers the greatest quality improvement per unit of total cost?

## Core papers

### Scaling Zero-Shot Reference-to-Video Generation (Saber)

- Paper: https://arxiv.org/abs/2512.06905
- Project page: https://franciszzj.github.io/Saber/
- Published on arXiv: 2025-12-07
- Main idea: a zero-shot R2V framework trained on video-text pairs without explicit reference-image/video/text triplets. It uses masked training and attention design to learn reference-aware, identity-consistent representations.
- Why it matters: targets the expensive data-pairing bottleneck and reports evaluation on OpenS2V-Eval.
- Read for: data scaling, reference awareness, copy-paste artifacts.

### RefAlign: Representation Alignment for Reference-to-Video Generation

- Paper: https://arxiv.org/abs/2603.25743
- Published on arXiv: 2026-03-26
- Main idea: aligns reference-branch features in a diffusion Transformer with the semantic space of a visual foundation model.
- Why it matters: addresses identity consistency, copy-paste artifacts, multi-subject confusion, and the trade-off between text controllability and reference fidelity.
- Read for: representation alignment and training objectives.

### OmniVBench: A Benchmark and Large-Scale Dataset for Omni Reference-to-Video Generation

- Paper: https://arxiv.org/abs/2609.22069
- Published on arXiv: 2026-09-18
- Main idea: benchmark and dataset for broader reference control, including content, motion, style, structure, narrative, and multi-reference settings.
- Why it matters: helps evaluate whether the generated video preserves the right reference factors and binds them to the right subjects, rather than only scoring overall visual similarity.

## Suggested reading order

1. **Saber** — understand how R2V can be learned without explicit R2V triplets.
2. **RefAlign** — understand how reference identity and semantic features can be aligned.
3. **OmniVBench** — understand how to test broader control and identify failure modes.

## Canonical research metadata

- [papers.yaml](papers.yaml) — structured paper catalog and review fields.
- [Survey and ablation plan](docs/ai-anime-production/survey-and-ablation.md) — use literature to decide what to include and what to remove.
- [LaTeX proposal](docs/ai-anime-production/paper-proposal.tex) — staged experiment and paper outline.

The catalog is a seed list, not an exhaustive or fully verified systematic survey. Verify bibliographic metadata, paper contents, model availability, licenses, inference requirements, and reproducibility from primary sources before making claims.

## Full-text paper RAG

A local-first retrieval pipeline for the three seed papers is available in [rag/](rag/README.md).

```bash
pip install -r rag/requirements.txt
python rag/r2v_rag.py ingest --download
python rag/r2v_rag.py ask "How do the papers handle identity consistency?"
```

The PDFs, extracted chunks, and full-text SQLite index stay local and are excluded from Git. Retrieval returns source paper, arXiv URL, and PDF page for every chunk. See [the RAG README](rag/README.md) for optional LLM generation and licensing notes.

## Published RAG databases

The GitHub Actions workflow builds and publishes two SQLite databases to GitHub Pages:

- Site: https://bonsai.github.io/r2v/
- Full-text paper index: https://bonsai.github.io/r2v/data/r2v_rag.sqlite3
- **Project RAG2 index:** https://bonsai.github.io/r2v/data/rag2.db
- Build workflow: [Build and publish R2V paper RAG](.github/workflows/rag.yml)

The full-text index contains paper chunks. RAG2 indexes the structured paper metadata in `papers.yaml` and the project research documents; it does **not** contain full-text PDF chunks. Both are generated artifacts, rebuilt by Actions rather than committed as binary files. Verify redistribution terms for the full-text index before public deployment. Configure Settings → Pages → Build and deployment → Source: GitHub Actions if needed.

## Research Explorer: four views

The static explorer presents the same canonical `site/research-map.json` data in four modes:

- **List** — browse papers and their keywords.
- **Graph** — explore paper-to-keyword relationships and filter by a keyword.
- **Digest** — read theme-based summaries and research questions.
- **Compare** — compare seed papers and recommendations in a table.

Select a mode in the UI or use `?view=list|graph|digest|compare`. Search and keyword filters are shared across modes. The OpenAPI 3.1 contract is in [openapi.yaml](openapi.yaml). Its `/papers/{paperId}`, `/graph`, `/digest`, and `/compare` paths describe a future API boundary; GitHub Pages currently serves static files only, so those paths are not live HTTP endpoints.

## AI anime production system

Reusable structured design package for Reference / Generation / Eval-JEV / TPS-Gate, including stick-figure motion control, YAML specifications, LoRA, and ML adapters.

- [Overview and index](docs/ai-anime-production/README.md)
- [HTML overview](docs/ai-anime-production/production-system.html)
- [SVG architecture](docs/ai-anime-production/production-system.svg)
- [Mermaid diagram](docs/ai-anime-production/production-system.mmd)
- [PlantUML diagram](docs/ai-anime-production/production-system.puml)
- [Canonical YAML](docs/ai-anime-production/production-system.yaml)
- [Research hypothesis](docs/ai-anime-production/hypothesis.md)
- [Paper outline](docs/ai-anime-production/paper-outline.md)
- [LaTeX proposal](docs/ai-anime-production/paper-proposal.tex)
- [Survey and ablation plan](docs/ai-anime-production/survey-and-ablation.md)

The combined LoRA + adapter + JEV feedback loop is a research hypothesis, not a validated result. The first experiment should be small and isolate variables.

## nwman: LAN-only network architecture

- [HTML overview](docs/ai-anime-production/nwman/network.html)
- [SVG network graph](docs/ai-anime-production/nwman/network.svg)
- [Mermaid graph](docs/ai-anime-production/nwman/network.mmd)
- [PlantUML graph](docs/ai-anime-production/nwman/network.puml)
- [Canonical topology YAML](docs/ai-anime-production/nwman/network.yaml)
- [Design notes and Kubernetes migration boundary](docs/ai-anime-production/nwman/README.md)

Network documents describe a logical private-LAN design, not an already deployed network.
