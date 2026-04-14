"""Tests for AI-QUAL-001: `any` type when specific type is inferrable."""

from tests.conftest import check_rule
from astray.rules.qual.qual001_any_type import AnyTypeOveruse


def test_any_annotation_flagged():
    src = "const data: any = await fetch('/api');\n"
    findings = check_rule(AnyTypeOveruse, src)
    assert len(findings) == 1
    assert findings[0].rule_id == "AI-QUAL-001"


def test_as_any_assertion_flagged():
    src = "const result = (input as any).value;\n"
    findings = check_rule(AnyTypeOveruse, src)
    assert len(findings) == 1


def test_return_type_any_flagged():
    src = "function process(): any { return {}; }\n"
    findings = check_rule(AnyTypeOveruse, src)
    assert len(findings) == 1


def test_proper_type_not_flagged():
    src = "const data: User[] = await fetchUsers();\n"
    findings = check_rule(AnyTypeOveruse, src)
    assert len(findings) == 0


def test_unknown_not_flagged():
    """unknown is the safe alternative to any and should not be flagged."""
    src = "const input: unknown = getInput();\n"
    findings = check_rule(AnyTypeOveruse, src)
    assert len(findings) == 0


def test_js_file_not_flagged():
    """any type rule only applies to TypeScript files."""
    src = "const x = 5;\n"
    findings = check_rule(AnyTypeOveruse, src, ext=".js")
    assert len(findings) == 0


def test_multiple_any_annotations_all_flagged():
    src = (
        "async function fetch(): Promise<any> {\n"
        "  const res: any = await call();\n"
        "  const data: any = res.json();\n"
        "  return data;\n"
        "}\n"
    )
    findings = check_rule(AnyTypeOveruse, src)
    assert len(findings) == 3
