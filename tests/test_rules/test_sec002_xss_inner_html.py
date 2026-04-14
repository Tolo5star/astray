"""Tests for AI-SEC-002: XSS via dangerouslySetInnerHTML or innerHTML."""

from tests.conftest import check_rule
from astray.rules.sec.sec002_xss_inner_html import XssDangerousHtml


def test_inner_html_assignment_flagged():
    src = (
        'function render(comment) {\n'
        '  const el = document.getElementById("root");\n'
        '  el.innerHTML = comment;\n'
        '}\n'
    )
    findings = check_rule(XssDangerousHtml, src)
    assert len(findings) == 1
    assert findings[0].line == 3


def test_dangerous_set_inner_html_with_variable_flagged():
    src = (
        'function App({ html }) {\n'
        '  return <div dangerouslySetInnerHTML={{ __html: html }} />;\n'
        '}\n'
    )
    findings = check_rule(XssDangerousHtml, src, ext=".tsx")
    assert len(findings) == 1
    assert findings[0].rule_id == "AI-SEC-002"


def test_dangerous_set_inner_html_static_template_not_flagged():
    """Static template literals (e.g. CSS injection) should not be flagged."""
    src = (
        'function Style() {\n'
        '  return <style dangerouslySetInnerHTML={{ __html: `\n'
        '    body { margin: 0; }\n'
        '  ` }} />;\n'
        '}\n'
    )
    findings = check_rule(XssDangerousHtml, src, ext=".tsx")
    assert len(findings) == 0


def test_dangerous_set_inner_html_static_string_not_flagged():
    """Plain static strings are safe."""
    src = (
        'const el = <div dangerouslySetInnerHTML={{ __html: "<b>bold</b>" }} />;\n'
    )
    findings = check_rule(XssDangerousHtml, src, ext=".tsx")
    assert len(findings) == 0


def test_text_content_not_flagged():
    """textContent assignment is safe."""
    src = (
        'function render(text) {\n'
        '  el.textContent = text;\n'
        '}\n'
    )
    findings = check_rule(XssDangerousHtml, src)
    assert len(findings) == 0


def test_inner_html_in_comment_not_flagged():
    src = '// el.innerHTML = userInput;\n'
    findings = check_rule(XssDangerousHtml, src)
    assert len(findings) == 0
