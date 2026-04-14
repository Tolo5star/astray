"""Tests for AI-LOGIC-001: Async function in array method."""

from tests.conftest import check_rule
from astray.rules.logic.logic001_async_in_array_method import AsyncInArrayMethod


def test_async_in_map_flagged():
    src = (
        "const results = items.map(async (item) => {\n"
        "  return await fetch(item);\n"
        "});\n"
    )
    findings = check_rule(AsyncInArrayMethod, src)
    assert len(findings) == 1
    assert findings[0].rule_id == "AI-LOGIC-001"


def test_async_in_filter_flagged():
    src = (
        "const valid = items.filter(async (item) => {\n"
        "  return await isValid(item);\n"
        "});\n"
    )
    findings = check_rule(AsyncInArrayMethod, src)
    assert len(findings) == 1


def test_async_in_foreach_flagged():
    src = (
        "items.forEach(async (item) => {\n"
        "  await process(item);\n"
        "});\n"
    )
    findings = check_rule(AsyncInArrayMethod, src)
    assert len(findings) == 1


def test_promise_all_wrapper_not_flagged():
    """async .map() inside Promise.all() is the correct pattern."""
    src = (
        "const results = await Promise.all(\n"
        "  items.map(async (item) => {\n"
        "    return await fetch(item);\n"
        "  })\n"
        ");\n"
    )
    findings = check_rule(AsyncInArrayMethod, src)
    assert len(findings) == 0


def test_sync_map_not_flagged():
    src = "const doubled = items.map((item) => item * 2);\n"
    findings = check_rule(AsyncInArrayMethod, src)
    assert len(findings) == 0


def test_multiple_async_maps_all_flagged():
    src = (
        "const a = xs.map(async (x) => await f(x));\n"
        "const b = ys.map(async (y) => await g(y));\n"
    )
    findings = check_rule(AsyncInArrayMethod, src)
    assert len(findings) == 2
