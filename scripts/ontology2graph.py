#!/usr/bin/env python3
"""Convert ontology.yml and optional instance YAML files into a deterministic graph YAML."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_yaml(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8")


def node(node_id: str, node_type: str, label: str, properties: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"id": node_id, "type": node_type, "label": label, "properties": properties or {}}


def edge(source: str, relation: str, target: str, properties: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": f"{source}--{relation}--{target}",
        "source": source,
        "type": relation,
        "target": target,
        "properties": properties or {},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ontology", default="ontology.yml")
    parser.add_argument("--mapping", default="rag2ontology.yml")
    parser.add_argument("--instances", default="instances")
    parser.add_argument("--output", default="graph/r2v.graph.yml")
    args = parser.parse_args()

    ontology_path = Path(args.ontology)
    ontology = load_yaml(ontology_path)
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []

    for name, definition in (ontology.get("concepts") or {}).items():
        node_id = f"concept:{name}"
        nodes[node_id] = node(node_id, "OntologyConcept", name, {
            "description": definition.get("description", ""),
            "properties": definition.get("properties", {}),
        })

    for name, definition in (ontology.get("relations") or {}).items():
        node_id = f"relation:{name}"
        nodes[node_id] = node(node_id, "OntologyRelation", name, {
            "domain": definition.get("domain"),
            "range": definition.get("range"),
        })
        domains = definition.get("domain", [])
        ranges = definition.get("range", [])
        domains = domains if isinstance(domains, list) else [domains]
        ranges = ranges if isinstance(ranges, list) else [ranges]
        for domain in domains:
            source = f"concept:{domain}"
            if source in nodes:
                edges[f"{source}--defines_relation--{node_id}"] = edge(source, "defines_relation", node_id)
            else:
                warnings.append(f"Unknown relation domain concept: {domain} ({name})")
        for range_type in ranges:
            range_types = range_type if isinstance(range_type, list) else [range_type]
            for item in range_types:
                target = f"concept:{item}"
                if target in nodes:
                    edges[f"{node_id}--allows_range--{target}"] = edge(node_id, "allows_range", target)
                else:
                    warnings.append(f"Unknown relation range concept: {item} ({name})")

    for record in ontology.get("research_records") or []:
        record_id = record.get("id")
        if not record_id:
            warnings.append("Skipped research record without id")
            continue
        record_type = record.get("type", "ResearchRecord")
        props = {k: v for k, v in record.items() if k not in {"id", "type", "method"}}
        nodes[record_id] = node(record_id, record_type, record.get("title", record_id), props)
        if record_type in (ontology.get("concepts") or {}):
            concept_id = f"concept:{record_type}"
            edges[f"{record_id}--instance_of--{concept_id}"] = edge(record_id, "instance_of", concept_id)
        nested_method = record.get("method")
        if isinstance(nested_method, dict) and nested_method.get("id"):
            method_id = nested_method["id"]
            nodes[method_id] = node(method_id, "Method", nested_method.get("name", method_id), {
                k: v for k, v in nested_method.items() if k not in {"id", "name"}
            })
            edges[f"{record_id}--has_method_record--{method_id}"] = edge(
                record_id, "has_method_record", method_id,
                {"note": "Nested method metadata from source record; not a verified ontology assertion."},
            )

    instance_root = Path(args.instances)
    if instance_root.exists():
        for path in sorted(instance_root.rglob("*.yml")) + sorted(instance_root.rglob("*.yaml")):
            try:
                payload = load_yaml(path)
            except (OSError, yaml.YAMLError) as exc:
                warnings.append(f"Could not parse {path}: {exc}")
                continue
            records = payload if isinstance(payload, list) else payload.get("instances", [payload]) if isinstance(payload, dict) else []
            for record in records:
                if not isinstance(record, dict) or not record.get("id"):
                    warnings.append(f"Skipped instance without id in {path}")
                    continue
                record_id = str(record["id"])
                record_type = str(record.get("type", "Instance"))
                nodes[record_id] = node(record_id, record_type, str(record.get("label") or record.get("title") or record_id), {
                    k: v for k, v in record.items() if k not in {"id", "type", "label", "title", "relations"}
                })
                for rel in record.get("relations", []) or []:
                    if not isinstance(rel, dict) or not rel.get("type") or not rel.get("target"):
                        warnings.append(f"Malformed relation in {path} for {record_id}")
                        continue
                    target = str(rel["target"])
                    rel_type = str(rel["type"])
                    edges[f"{record_id}--{rel_type}--{target}"] = edge(record_id, rel_type, target, rel.get("properties", {}))

    unresolved = []
    for item in edges.values():
        if item["source"] not in nodes or item["target"] not in nodes:
            unresolved.append({"edge_id": item["id"], "source": item["source"], "target": item["target"]})

    graph = {
        "graph": {
            "id": "bonsai.r2v.graph",
            "directed": True,
            "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
            "edges": sorted(edges.values(), key=lambda item: item["id"]),
            "metadata": {
                "source_files": [str(ontology_path)] + ([args.mapping] if Path(args.mapping).exists() else []),
                "ontology_version": (ontology.get("ontology") or {}).get("version"),
                "warnings": warnings,
                "unresolved_references": unresolved,
            },
        }
    }
    dump_yaml(Path(args.output), graph)
    dump_yaml(Path("graph/unresolved-references.yml"), {"unresolved_references": unresolved, "warnings": warnings})
    print(json.dumps({
        "output": args.output,
        "nodes": len(nodes),
        "edges": len(edges),
        "unresolved_references": len(unresolved),
        "warnings": len(warnings),
    }, ensure_ascii=False))
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
