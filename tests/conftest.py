"""Shared test fixtures and helpers for Astray rule tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from astray.parsers.typescript import TypeScriptParser
from astray.models import Finding

FAKE_PATH = Path("test_file.ts")
FAKE_TSX_PATH = Path("test_file.tsx")

_parser = TypeScriptParser()


def parse_ts(source: str, ext: str = ".ts"):
    """Parse a TypeScript/JS snippet and return (root_node, source_bytes)."""
    return _parser.parse_bytes(source.encode(), ext=ext)


def check_rule(rule_class, source: str, ext: str = ".ts") -> list[Finding]:
    """Instantiate a rule and run it against a source snippet."""
    path = Path(f"test_file{ext}")
    root, src_bytes = parse_ts(source, ext=ext)
    return rule_class().check(root, src_bytes, path)


def finding_lines(findings: list[Finding]) -> list[int]:
    """Extract line numbers from a list of findings."""
    return [f.line for f in findings]


def finding_rule_ids(findings: list[Finding]) -> list[str]:
    return [f.rule_id for f in findings]
