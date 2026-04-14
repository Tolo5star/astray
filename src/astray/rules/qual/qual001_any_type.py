"""
AI-QUAL-001: `any` type used when a specific type is inferrable

AI generators default to `: any` when they can't determine the type,
producing code like `const data: any = await fetch(...)`. This defeats
TypeScript's type system and hides bugs.

Fix: Replace with the actual type, `unknown`, or a generic.
Source: Common AI anti-pattern, 1.64x maintainability issues (CodeRabbit)
"""

from __future__ import annotations

from pathlib import Path

from tree_sitter import Node

from astray.models import Finding, RuleMeta, Severity
from astray.rules.base import Rule
from astray.rules.registry import register


@register
class AnyTypeOveruse(Rule):

    meta = RuleMeta(
        id="AI-QUAL-001",
        name="`any` type when specific type is inferrable",
        description=(
            "Using `: any` defeats TypeScript's type system. AI generators "
            "default to `any` when unsure of the type."
        ),
        severity=Severity.WARNING,
        multiplier="1.64x",
        source="CodeRabbit Report — 1.64x maintainability issues in AI code",
        languages=("typescript",),
    )

    def check(self, root: Node, source: bytes, file_path: Path) -> list[Finding]:
        # Only applies to TypeScript files
        if file_path.suffix not in (".ts", ".tsx", ".mts"):
            return []

        findings: list[Finding] = []

        # Walk all predefined_type nodes — covers both direct annotations
        # (`: any`) and generic type arguments (`Promise<any>`, `Array<any>`).
        seen: set[int] = set()
        for node in self.find_all(root, "predefined_type"):
            if source[node.start_byte:node.end_byte] != b"any":
                continue
            # Deduplicate (node may be visited multiple times by the walker)
            if node.start_byte in seen:
                continue
            # Only flag when inside a type context, not a value expression
            if not self._in_type_context(node):
                continue
            seen.add(node.start_byte)
            findings.append(self._make_finding(
                file_path, node, source,
                message="`any` type used — specific type is likely inferrable",
                fix="Replace with the actual type, `unknown`, or a generic parameter",
            ))

        # Also catch `as any` type assertions
        for node in self.find_all(root, "as_expression"):
            for child in node.children:
                if child.type == "predefined_type":
                    if source[child.start_byte:child.end_byte] == b"any":
                        findings.append(self._make_finding(
                            file_path, child, source,
                            message="`as any` type assertion — bypasses type safety",
                            fix="Use a proper type assertion or fix the underlying type mismatch",
                        ))

        return findings

    @staticmethod
    def _in_type_context(node: Node) -> bool:
        """Return True if a node lives inside a type annotation or type argument."""
        _TYPE_PARENTS = frozenset({
            "type_annotation", "type_arguments", "return_type",
            "type_predicate_annotation", "type_alias_declaration",
            "function_type", "union_type", "intersection_type",
            "parenthesized_type", "array_type", "readonly_type",
        })
        parent = node.parent
        while parent is not None:
            if parent.type in _TYPE_PARENTS:
                return True
            if parent.type in ("expression_statement", "program"):
                break
            parent = parent.parent
        return False
