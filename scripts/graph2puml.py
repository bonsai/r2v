#!/usr/bin/env python3
"""Render a normalized R2V graph YAML file as safe, deterministic PlantUML."""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def quote(value: Any) -> str:
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return re.sub(r"[\r\n]+", " ", text)


def alias(node_id: str) -> str:
    base = re.sub(r"[^A-Za-z0-9_]", "_", node_id)
    if not base or not base[0].isalpha():
        base = "N_" + base
    # A short stable suffix prevents sanitized IDs from colliding.
    suffix = hashlib.sha1(node_id.encode("utf-8")).hexdigest()[:6]
    return f"N_{base}_{suffix}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="graph/r2v.graph.yml")
    parser.add_argument("--output", default="diagrams/r2v.puml")
    args = parser.parse_args()

    payload = load_yaml(Path(args.input))
    graph = payload.get("graph", payload)
    nodes = graph.get("nodes", []) or []
    edges = graph.get("edges", []) or []
    known = {str(n["id"]): n for n in nodes if isinstance(n, dict) and n.get("id") is not None}
    aliases = {node_id: alias(node_id) for node_id in known}
    lines = [
        "@startuml",
        "left to right direction",
        "skinparam classAttributeIconSize 0",
        "skinparam linetype ortho",
        "",
    ]
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in sorted(known.values(), key=lambda n: (str(n.get("type", "Node")), str(n["id"]))):
        groups.setdefault(str(item.get("type", "Node")), []).append(item)

    for group, items in sorted(groups.items()):
        safe_group = re.sub(r"[^A-Za-z0-9_]", "_", group) or "Other"
        lines.append(f'package "{quote(group)}" as P_{safe_group} {{')
        for item in items:
            node_id = str(item["id"])
            label = quote(item.get("label") or node_id)
            lines.append(f'class "{label}" as {aliases[node_id]} <<{quote(item.get("type", "Node"))}>> {{')
            props = item.get("properties") or {}
            if isinstance(props, dict):
                for key in ("arxiv_id", "verification_status", "page", "confidence", "description"):
                    if key in props and props[key] not in (None, ""):
                        value = quote(props[key])
                        lines.append(f"  {key} : {value}")
            lines.append("}")
        lines.append("}")
        lines.append("")

    missing = []
    for item in sorted(edges, key=lambda e: (str(e.get("source")), str(e.get("type")), str(e.get("target")))):
        source, target = str(item.get("source", "")), str(item.get("target", ""))
        if source not in aliases or target not in aliases:
            missing.append(item.get("id", f"{source}->{target}"))
            continue
        label = quote(item.get("type", "related_to"))
        lines.append(f"{aliases[source]} --> {aliases[target]} : {label}")

    lines.extend(["", "@enduml", ""])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    if missing:
        Path("diagrams/unrendered-edges.txt").write_text("\n".join(map(str, missing)) + "\n", encoding="utf-8")
    print(f"Rendered {len(known)} nodes and {len(edges) - len(missing)} edges to {output}")
    if missing:
        print(f"Skipped {len(missing)} edges with missing endpoints")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
