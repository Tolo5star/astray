"""Tests for AI-SEC-004: Over-permissive CORS wildcard origin."""

from tests.conftest import check_rule
from astray.rules.sec.sec004_cors_wildcard import CorsWildcard


def test_cors_wildcard_origin_flagged():
    src = "app.use(cors({ origin: '*' }));"
    findings = check_rule(CorsWildcard, src)
    assert len(findings) == 1
    assert findings[0].rule_id == "AI-SEC-004"


def test_cors_specific_origin_not_flagged():
    src = 'app.use(cors({ origin: "https://myapp.com" }));'
    findings = check_rule(CorsWildcard, src)
    assert len(findings) == 0


def test_cors_array_origins_not_flagged():
    src = 'app.use(cors({ origin: ["https://myapp.com", "https://staging.myapp.com"] }));'
    findings = check_rule(CorsWildcard, src)
    assert len(findings) == 0


def test_access_control_header_wildcard_flagged():
    src = 'res.setHeader("Access-Control-Allow-Origin", "*");'
    findings = check_rule(CorsWildcard, src)
    assert len(findings) == 1


def test_access_control_header_specific_not_flagged():
    src = 'res.setHeader("Access-Control-Allow-Origin", "https://myapp.com");'
    findings = check_rule(CorsWildcard, src)
    assert len(findings) == 0
