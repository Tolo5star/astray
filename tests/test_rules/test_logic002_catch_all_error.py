"""Tests for AI-LOGIC-002: Catch-all error handling that swallows errors."""

from tests.conftest import check_rule
from astray.rules.logic.logic002_catch_all_error import CatchAllError


def test_empty_catch_flagged():
    src = (
        "try {\n"
        "  doSomething();\n"
        "} catch (e) {\n"
        "}\n"
    )
    findings = check_rule(CatchAllError, src)
    assert len(findings) == 1
    assert findings[0].rule_id == "AI-LOGIC-002"
    assert "silently swallowed" in findings[0].message


def test_log_only_catch_flagged():
    src = (
        "try {\n"
        "  doSomething();\n"
        "} catch (error) {\n"
        "  console.log(error);\n"
        "}\n"
    )
    findings = check_rule(CatchAllError, src)
    assert len(findings) == 1
    assert "only logs" in findings[0].message


def test_console_error_only_catch_flagged():
    src = (
        "try {\n"
        "  doSomething();\n"
        "} catch (err) {\n"
        "  console.error(err);\n"
        "}\n"
    )
    findings = check_rule(CatchAllError, src)
    assert len(findings) == 1


def test_rethrow_catch_not_flagged():
    src = (
        "try {\n"
        "  doSomething();\n"
        "} catch (error) {\n"
        "  console.error(error);\n"
        "  throw error;\n"
        "}\n"
    )
    findings = check_rule(CatchAllError, src)
    assert len(findings) == 0


def test_handled_catch_not_flagged():
    src = (
        "try {\n"
        "  doSomething();\n"
        "} catch (error) {\n"
        "  setError(error.message);\n"
        "  notify(error);\n"
        "}\n"
    )
    findings = check_rule(CatchAllError, src)
    assert len(findings) == 0


def test_multiple_catches_each_checked():
    src = (
        "async function a() {\n"
        "  try { await x(); } catch {}\n"
        "}\n"
        "async function b() {\n"
        "  try { await y(); } catch (e) { console.log(e); }\n"
        "}\n"
        "async function c() {\n"
        "  try { await z(); } catch (e) { throw e; }\n"
        "}\n"
    )
    findings = check_rule(CatchAllError, src)
    # a() empty catch + b() log-only catch are flagged, c() rethrow is not
    assert len(findings) == 2
