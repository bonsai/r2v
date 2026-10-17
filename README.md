# R2V Research Notes

Research notes for Reference-to-Video (R2V) generation: generating a video that follows a text prompt while preserving or controlling information from reference images.

> Scope note: this repository was empty when these notes were added. The papers below are a starting-point literature map, not an assertion that this is the project's final intended scope.

## Research questions

- How can a model preserve the identity of a person or object from reference images across generated frames?
- How can it follow text instructions without copying reference pixels into the video?
- How should multiple reference images and different factors (content, motion, style, structure, narrative) be controlled independently?
- What data and evaluation protocols are needed to measure reference fidelity and instruction following?

## Core papers

### Scaling Zero-Shot Reference-to-Video Generation (Saber)

- Paper: https://arxiv.org/abs/2512.06905
- Project page: https://franciszzj.github.io/Saber/
- Published on arXiv: 2025-12-07
- Main idea: a zero-shot R2V framework trained on video-text pairs without explicit reference-image/video/text triplets. It uses masked training and attention design to learn reference-aware, identity-consistent representations.
- Why it matters: targets the expensive data-pairing bottleneck and reports evaluation on OpenS2V-Eval.
- Read for: data scaling, masked training, reference awareness, copy-paste artifacts.

### RefAlign: Representation Alignment for Reference-to-Video Generation

- Paper: https://arxiv.org/abs/2603.25743
- Published on arXiv: 2026-03-26
- Main idea: aligns reference-branch features in a diffusion Transformer with the semantic space of a visual foundation model. A training-time alignment loss encourages same-subject features to be closer and different-subject features to be more distinguishable.
- Why it matters: addresses identity consistency, copy-paste artifacts, multi-subject confusion, and the trade-off between text controllability and reference fidelity.
- Read for: representation alignment and training objectives; the approach is designed not to add inference-time overhead.

### OmniVBench: A Benchmark and Large-Scale Dataset for Omni Reference-to-Video Generation

- Paper: https://arxiv.org/abs/2609.22069
- Published on arXiv: 2026-09-18
- Main idea: benchmark and dataset for broader reference control, including content, motion, style, structure, narrative, and multi-reference settings. The paper describes seven task families and 18 fine-grained tasks, with factor-grounded evaluation.
- Why it matters: helps evaluate whether a model preserves the *right* reference factors and binds them to the right subjects, rather than only scoring overall visual similarity.
- Read for: evaluation design, dataset construction, multi-reference control.

## Suggested reading order

1. **Saber** — understand how R2V can be learned without explicit R2V triplets.
2. **RefAlign** — understand how reference identity and semantic features can be aligned during training.
3. **OmniVBench** — understand how to test broader control and identify failure modes.

## Initial comparison

| Paper | Main focus | Useful question |
|---|---|---|
| Saber | Training/data scalability | Can reference-aware generation be learned from video-text pairs alone? |
| RefAlign | Feature alignment | Can identity consistency improve without sacrificing text control? |
| OmniVBench | Evaluation/data | Does the generated video preserve the requested reference factors and assign them correctly? |

## Suggested next steps

- Verify each paper's method, datasets, metrics, and limitations from the full paper before implementing anything.
- Record model availability, license, inference requirements, and reproducibility notes in a separate comparison file.
- If this repository targets a different meaning of R2V, revise the scope before expanding this bibliography.

## Sources

- Zhou et al., *Scaling Zero-Shot Reference-to-Video Generation*, arXiv:2512.06905.
- Wang et al., *RefAlign: Representation Alignment for Reference-to-Video Generation*, arXiv:2603.25743.
- Li et al., *OmniVBench: A Benchmark and Large-Scale Dataset for Omni Reference-to-Video Generation*, arXiv:2609.22069.


## Full-text paper RAG

A local-first retrieval pipeline for the three papers is available in [`rag/`](rag/README.md).

```bash
pip install -r rag/requirements.txt
python rag/r2v_rag.py ingest --download
python rag/r2v_rag.py ask "How do the papers handle identity consistency?"
```

The PDFs, extracted chunks, and SQLite index stay local and are excluded from Git. Retrieval returns source paper, arXiv URL, and PDF page for every chunk. See [the RAG README](rag/README.md) for optional LLM generation and licensing notes.


## Published RAG database

The GitHub Actions workflow rebuilds the SQLite index and publishes the site and database to GitHub Pages:

- Site: https://bonsai.github.io/r2v/
- Download database: https://bonsai.github.io/r2v/data/r2v_rag.sqlite3
- Workflow: [Build and publish R2V paper RAG](.github/workflows/rag.yml)

The published SQLite database contains extracted full-text chunks. Before making the site public, verify the license and redistribution terms for all three papers. If the repo's Pages settings do not use **GitHub Actions** as the build/deploy source, configure Settings → Pages → Build and deployment → Source: GitHub Actions.


## Research Explorer: four views

The static explorer presents the same canonical `site/research-map.json` data in four modes:

- **List** — browse papers and their keywords.
- **Graph** — explore paper-to-keyword relationships and filter by a keyword.
- **Digest** — read theme-based summaries and research questions.
- **Compare** — compare seed papers and recommendations in a table.

Select a mode in the UI or use `?view=list|graph|digest|compare`. Search and keyword filters are shared across modes. The OpenAPI 3.1 contract is in [`openapi.yaml`](openapi.yaml). Its `/papers/{paperId}`, `/graph`, `/digest`, and `/compare` paths describe a future API boundary; GitHub Pages currently serves static files only, so those paths are not live HTTP endpoints.


## AI anime production system

Reusable structured design package for Reference / Generation / Eval-JEV / TPS-Gate, including stick-figure motion control, YAML specifications, LoRA, and ML adapters.

- [Overview and index](docs/ai-anime-production/README.md)
- [HTML overview](docs/ai-anime-production/production-system.html)
- [SVG architecture](docs/ai-anime-production/production-system.svg)
- [Mermaid diagram](docs/ai-anime-production/production-system.mmd)
- [PlantUML diagram](docs/ai-anime-production/production-system.puml)
- [Canonical YAML](docs/ai-anime-production/production-system.yaml)

The LoRA + adapter + JEV feedback loop is a research hypothesis, not a validated result. See the package for the staged comparison plan.


### Research hypothesis: Software Factory × R2V × TPS × ML/Kaggle

- [Full hypothesis and staged experiment plan](docs/ai-anime-production/hypothesis.md)
- [AI anime production system package](docs/ai-anime-production/README.md)

The combined architecture is a research hypothesis, not a proven result. The plan starts with one R2V baseline and adds controls and evaluation one at a time.
