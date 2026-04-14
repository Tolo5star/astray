"""Tests for AI-QUAL-003: Unused imports from incomplete AI refactors."""

from tests.conftest import check_rule
from astray.rules.qual.qual003_unused_imports import UnusedImports


def test_unused_named_import_flagged():
    src = (
        "import { useState, useEffect } from 'react';\n"
        "export default function App() { return null; }\n"
    )
    findings = check_rule(UnusedImports, src, ext=".tsx")
    rule_findings = [f for f in findings if f.rule_id == "AI-QUAL-003"]
    flagged_names = [f.message for f in rule_findings]
    assert any("useState" in m for m in flagged_names)
    assert any("useEffect" in m for m in flagged_names)


def test_used_import_not_flagged():
    src = (
        "import { useState } from 'react';\n"
        "export default function App() {\n"
        "  const [x, setX] = useState(0);\n"
        "  return null;\n"
        "}\n"
    )
    findings = check_rule(UnusedImports, src, ext=".tsx")
    assert not any("useState" in f.message for f in findings)


def test_unused_default_import_flagged():
    src = (
        "import Footer from './Footer';\n"
        "export default function Page() { return <main/>; }\n"
    )
    findings = check_rule(UnusedImports, src, ext=".tsx")
    assert any("Footer" in f.message for f in findings)


def test_used_default_import_not_flagged():
    src = (
        "import Footer from './Footer';\n"
        "export default function Page() { return <Footer />; }\n"
    )
    findings = check_rule(UnusedImports, src, ext=".tsx")
    assert not any("Footer" in f.message for f in findings)


def test_type_only_import_not_flagged():
    """Type-only imports are stripped at compile time and are fine."""
    src = (
        "import type { User } from './types';\n"
        "function greet(u: User) { return u.name; }\n"
    )
    findings = check_rule(UnusedImports, src)
    assert not any("User" in f.message for f in findings)


def test_partial_import_flags_only_unused():
    src = (
        "import { useRouter, usePathname } from 'next/navigation';\n"
        "export default function Nav() {\n"
        "  const router = useRouter();\n"
        "  return null;\n"
        "}\n"
    )
    findings = check_rule(UnusedImports, src, ext=".tsx")
    flagged = [f.message for f in findings if f.rule_id == "AI-QUAL-003"]
    assert any("usePathname" in m for m in flagged)
    assert not any("useRouter" in m for m in flagged)
