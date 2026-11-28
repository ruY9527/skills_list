#!/usr/bin/env python3
"""AST-based PyTorch repository scanner for HSI-MSI & Vision repos.

Quickly locates nn.Module classes, forward() signatures, loss classes, and
training/inference entry scripts without importing third-party dependencies.

Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from typing import Any

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "build", "dist", ".mypy_cache"}


def get_base_names(node: ast.ClassDef) -> list[str]:
    names: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            parts = []
            cur: ast.AST = base
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            names.append(".".join(reversed(parts)))
    return names


def scan_python_file(path: str, rel_path: str) -> dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=path)
    except SyntaxError:
        return None

    modules: list[dict[str, Any]] = []
    has_main = False

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = get_base_names(node)
            is_nn = any("Module" in b for b in bases)
            forward_args: list[str] = []
            forward_line: int | None = None
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "forward":
                    forward_args = [a.arg for a in item.args.args if a.arg != "self"]
                    forward_line = item.lineno
            if is_nn or forward_line is not None or "loss" in node.name.lower():
                modules.append(
                    {
                        "class_name": node.name,
                        "bases": bases,
                        "line_start": node.lineno,
                        "line_end": getattr(node, "end_lineno", node.lineno),
                        "forward_line": forward_line,
                        "forward_args": forward_args,
                    }
                )
        elif isinstance(node, ast.If):
            # Detect if __name__ == "__main__":
            test_str = ast.unparse(node.test) if hasattr(ast, "unparse") else ""
            if "__main__" in test_str:
                has_main = True

    if not modules and not has_main:
        return None
    return {"file": rel_path, "has_main_entry": has_main, "modules": modules}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan a PyTorch repository for nn.Module classes and entry points.")
    parser.add_argument("--repo", required=True, help="Path to the target repository root.")
    parser.add_argument("--output", default=None, help="Optional JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = os.path.abspath(args.repo)
    if not os.path.isdir(repo_root):
        print(f"Error: Directory not found: {repo_root}", file=sys.stderr)
        return 2

    files_report: list[dict[str, Any]] = []
    total_py = 0

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            total_py += 1
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, repo_root).replace("\\", "/")
            entry = scan_python_file(full_path, rel_path)
            if entry:
                files_report.append(entry)

    payload = {
        "repo_root": repo_root,
        "total_python_files_scanned": total_py,
        "files_with_modules_or_entries": len(files_report),
        "entries": files_report,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Scanned {total_py} Python files; saved repo map to {args.output}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
