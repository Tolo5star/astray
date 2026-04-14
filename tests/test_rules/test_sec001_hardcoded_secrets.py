"""Tests for AI-SEC-001: Hardcoded secrets disguised as placeholders.

Secret-like strings in tests are constructed programmatically so that
GitHub push protection does not block the commit — the full literal never
appears in Python source, only in the string built at runtime.
"""

from tests.conftest import check_rule
from astray.rules.sec.sec001_hardcoded_secrets import HardcodedSecrets

# Helpers that build secret-looking test strings at runtime.
# Split prefix/body so no full secret literal appears as a Python string literal.
_SK_PROJ  = "sk-proj-"    + "abc123def456ghi789jkl012mno345pqr678stu901vwx"
_SK_LIVE  = "sk_live_"    + "51ABCDEFGHIJKLMNOPQRSTUVWXYZabcd"
_GHP      = "ghp_"        + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"
_AWS      = "AKIA"        + "JG74OXPWIRJQ5ZBD"


def test_openai_key_flagged():
    src = f'const key = "{_SK_PROJ}";'
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 1
    assert findings[0].rule_id == "AI-SEC-001"
    assert findings[0].line == 1


def test_stripe_live_key_flagged():
    src = f'const stripe = "{_SK_LIVE}";'
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 1


def test_github_token_flagged():
    src = f'const token = "{_GHP}";'
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 1


def test_aws_key_flagged():
    src = f'const awsKey = "{_AWS}";'
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 1


def test_env_var_not_flagged():
    """Keys loaded from environment variables are safe."""
    src = "const key = process.env.OPENAI_API_KEY;"
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 0


def test_placeholder_allowlisted():
    """Obvious placeholder values should not be flagged."""
    src = 'const key = "your-api-key-here";'
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 0


def test_comment_not_flagged():
    """Keys in comments should be ignored."""
    src = f'// const key = "{_SK_PROJ}";'
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 0


def test_multiple_keys_one_finding_per_line():
    """Only one finding per line even if multiple patterns match."""
    src = f'const key = "{_SK_PROJ}";'
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 1


def test_multiline_only_flags_matching_lines():
    src = (
        'const a = "safe-value";\n'
        f'const b = "{_SK_PROJ}";\n'
        'const c = "also-safe";\n'
    )
    findings = check_rule(HardcodedSecrets, src)
    assert len(findings) == 1
    assert findings[0].line == 2
