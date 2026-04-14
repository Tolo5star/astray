"""Tests for the Scanner engine — file discovery, multi-rule, ignore globs."""

from pathlib import Path

import pytest

from astray.config import VibelintConfig
from astray.engine import Scanner
from astray.models import Severity


FIXTURES = Path(__file__).parent / "fixtures"


def test_scan_bad_fixture_has_findings():
    scanner = Scanner()
    result = scanner.scan(FIXTURES / "bad_vibes.ts")
    assert result.files_scanned == 1
    assert result.critical_count > 0
    assert result.warning_count > 0
    assert len(result.findings) > 0


def test_scan_clean_fixture_has_no_findings():
    scanner = Scanner()
    result = scanner.scan(FIXTURES / "clean_code.ts")
    assert result.files_scanned == 1
    assert len(result.findings) == 0


def test_scan_directory_counts_both_files():
    scanner = Scanner()
    result = scanner.scan(FIXTURES)
    assert result.files_scanned == 2


def test_findings_sorted_critical_first():
    scanner = Scanner()
    result = scanner.scan(FIXTURES / "bad_vibes.ts")
    severities = [f.severity for f in result.findings]
    # Critical findings should come before warnings
    seen_warning = False
    for sev in severities:
        if sev == Severity.WARNING:
            seen_warning = True
        if seen_warning:
            assert sev != Severity.CRITICAL, "Critical finding appeared after warning"


def test_config_disable_rule():
    from astray.config import RuleConfig
    config = VibelintConfig(
        rules={"AI-SEC-001": RuleConfig(enabled=False)}
    )
    scanner = Scanner(config)
    result = scanner.scan(FIXTURES / "bad_vibes.ts")
    rule_ids = {f.rule_id for f in result.findings}
    assert "AI-SEC-001" not in rule_ids


def test_config_severity_override():
    from astray.config import RuleConfig
    config = VibelintConfig(
        rules={"AI-LOGIC-001": RuleConfig(severity=Severity.INFO)}
    )
    scanner = Scanner(config)
    result = scanner.scan(FIXTURES / "bad_vibes.ts")
    logic001 = [f for f in result.findings if f.rule_id == "AI-LOGIC-001"]
    assert all(f.severity == Severity.INFO for f in logic001)


def test_unsupported_file_skipped(tmp_path):
    py_file = tmp_path / "script.py"
    py_file.write_text("x: any = 5\n")
    scanner = Scanner()
    result = scanner.scan(py_file)
    assert result.files_scanned == 0


def test_ignore_glob_excludes_files(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "dist").mkdir()
    (tmp_path / "src" / "app.ts").write_text(
        'const key = "sk-proj-abc123def456ghi789jkl012mno345pqr678stu";\n'
    )
    (tmp_path / "dist" / "app.js").write_text(
        'const key = "sk-proj-abc123def456ghi789jkl012mno345pqr678stu";\n'
    )
    scanner = Scanner()  # default ignores include dist/**
    result = scanner.scan(tmp_path)
    files_scanned = [f.file for f in result.findings]
    assert not any("dist" in str(p) for p in files_scanned)
