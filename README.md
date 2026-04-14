# Astray

**AI code pattern scanner. Catch the bugs AI writes 2.74x more often.**

Research-backed rules targeting the specific ways AI generators fail. Not a generic linter — a scanner that knows *how* AI fails and flags those exact patterns, with the multiplier to prove it.

```bash
pip install astray
astray scan ./src
```

```
astray v0.1.0 — AI Code Pattern Scanner
117 files scanned · 9 critical · 418 warning · 0 info

───────────────────── CRITICAL  9 issues ──────────────────────

  hooks/useLocalStorage.ts  2 issues
  ├─ line 36  AI-LOGIC-002  Catch block only logs — error is not re-thrown
  │     } catch (error) {
  │    → Re-throw after logging, or handle the error condition explicitly
  │    AI generates this 1.75x more often
  │
  └─ line 81  AI-LOGIC-002  Catch block only logs — error is not re-thrown

  lib/api/stats.ts  2 issues
  ├─ line 44  AI-LOGIC-002  Empty catch block — errors are silently swallowed
  └─ line 67  AI-LOGIC-002  Empty catch block — errors are silently swallowed

───────────────────── WARNING  418 issues ─────────────────────

  Rule          What it flags             Issues  Files  Worst file
  AI-QUAL-003   'Footer' is imported         364     91  GameRoot.tsx (24)
  AI-LOGIC-004  'obj' may be undefined        30      6  missions/page.tsx (8)
  AI-QUAL-001   as any type assertion         24     13  lib/auth.ts (5)

──────────────────────────────────────────────────────────────
  9 critical · 418 warning  in 117 files
  Run with --verbose to expand all warnings
```

---

## Why Astray

AI-generated code fails in statistically predictable patterns that generic linters miss:

| Pattern | AI vs Human |
|---------|-------------|
| XSS vulnerabilities | **2.74x** more likely |
| Insecure credential handling | **1.88x** more likely |
| Logic / correctness errors | **1.75x** more likely |
| Maintainability issues | **1.64x** more likely |
| Security findings (general) | **1.57x** more likely |

Sources: [CodeRabbit AI vs Human Code Report (Dec 2025)](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report), [CMU Security Benchmark (2026)](https://dev.to/solobillions/i-tested-every-vibe-coding-security-scanner-2026-heres-what-actually-works-p9k)

**Astray is not:**
- A generic linter (ESLint, Pylint do that)
- A SAST scanner (Semgrep, Snyk do that)
- An AI code detector (SonarQube does that)

**Astray is:** a scanner that knows the documented failure profile of AI generators and catches exactly those patterns.

---

## Installation

> **PyPI release coming soon.** Install from source in the meantime:

```bash
git clone https://github.com/Tolo5star/astray
cd astray
pip install -e .
```

**Requirements:** Python 3.10+

---

## Usage

### Scan a directory

```bash
astray scan ./src
```

### Scan a single file

```bash
astray scan src/api/auth.ts
```

### JSON output (for CI/CD pipelines, dashboards)

```bash
astray scan ./src --format json
```

### Fail on specific severity (for CI gates)

```bash
# Exit 1 if any critical finding
astray scan ./src --fail-on critical

# Exit 1 if any warning or above
astray scan ./src --fail-on warning
```

### Expand all warnings

```bash
astray scan ./src --verbose
```

### List all rules

```bash
astray rules
```

---

## Rules

8 research-backed rules in v0.1.0, targeting TypeScript and JavaScript.

### Security

| Rule | Pattern | Multiplier | Severity |
|------|---------|-----------|---------|
| `AI-SEC-001` | Hardcoded secrets disguised as placeholders (`sk-placeholder-xxx`, `sk_live_...`) | 1.88x | Critical |
| `AI-SEC-002` | XSS via `dangerouslySetInnerHTML` with dynamic value or direct `.innerHTML =` | 2.74x | Critical |
| `AI-SEC-004` | Over-permissive CORS (`origin: '*'`) | 1.57x | Warning |

### Logic

| Rule | Pattern | Multiplier | Severity |
|------|---------|-----------|---------|
| `AI-LOGIC-001` | Async function in `.map()` / `.filter()` returns `Promise[]`, not resolved values | 1.75x | Critical |
| `AI-LOGIC-002` | Empty catch block or catch that only `console.log`s (swallows errors silently) | 1.75x | Critical |
| `AI-LOGIC-004` | Missing null check after `.find()` / `.at()` / `.get()` (value may be `undefined`) | 1.75x | Warning |

### Quality

| Rule | Pattern | Multiplier | Severity |
|------|---------|-----------|---------|
| `AI-QUAL-001` | `: any` type annotation or `as any` assertion (TypeScript only) | 1.64x | Warning |
| `AI-QUAL-003` | Unused import — leftover from AI mid-generation refactor | 1.64x | Warning |

**Smart suppressions:**
- `AI-LOGIC-001` skips `.map()` calls already wrapped in `Promise.all()`
- `AI-SEC-002` skips `dangerouslySetInnerHTML` when `__html` is a static string/template (e.g. CSS-in-JS `<style>` injection) — only flags variable/expression values

---

## Configuration

Create `.astray.yaml` in your project root:

```yaml
rules:
  AI-QUAL-001:
    severity: info      # downgrade to info for this project
  AI-QUAL-003:
    enabled: false      # disable entirely
  AI-SEC-001:
    severity: critical  # keep as critical (default)

ignore:
  - "node_modules/**"
  - "dist/**"
  - "**/*.test.ts"
  - "**/*.spec.ts"

fail_on: warning        # exit 1 if any warning or above
```

Astray walks up from the scan target to find `.astray.yaml`. If none is found, defaults are used.

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/astray.yml
name: Astray

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install astray
      - run: astray scan ./src --fail-on critical
```

### GitLab CI

```yaml
astray:
  image: python:3.12
  script:
    - pip install astray
    - astray scan ./src --fail-on critical
```

### Pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: astray
        name: Astray AI pattern scan
        entry: astray scan
        args: [--fail-on, critical]
        language: python
        pass_filenames: false
```

---

## How It Works

Astray uses [tree-sitter](https://tree-sitter.github.io/tree-sitter/) to parse TypeScript/JavaScript into an AST, then runs pattern-matching rules against the tree.

```
Source files
    │
    ▼
tree-sitter parser  ──▶  AST
    │
    ▼
Rules (AST matching + regex)  ──▶  Findings[]
    │
    ▼
Formatter (terminal / JSON)  ──▶  Output
```

- **One parse per file, all rules run on the same AST** — fast even on large codebases
- **AST-based matching** catches structural patterns regardless of formatting or indentation
- **Regex fallback** for textual patterns (secrets, CORS headers) where AST is overkill
- Each rule carries its **research citation and failure multiplier** — findings explain *why* this is a problem, not just that it is one

---

## Supported Languages

| Language | Status |
|----------|--------|
| TypeScript (`.ts`, `.mts`) | v0.1 |
| TypeScript JSX (`.tsx`) | v0.1 |
| JavaScript (`.js`, `.mjs`) | v0.1 |
| JavaScript JSX (`.jsx`) | v0.1 |
| Python | v0.2 (planned) |
| Go | v0.3 (planned) |

---

## Roadmap

| Version | What |
|---------|------|
| v0.1 | 8 rules, TS/JS/TSX/JSX, CLI, JSON output |
| v0.2 | Python target language, 30+ rules, GitHub Action |
| v0.3 | Community rule contributions, rule marketplace |
| v0.4 | VS Code / JetBrains extensions |
| v1.0 | Team dashboard, AI debt tracking over time |

---

## Contributing

Rules live in `src/astray/rules/{sec,logic,qual}/`. Each rule is a Python class:

```python
from astray.rules.base import Rule
from astray.rules.registry import register
from astray.models import RuleMeta, Severity

@register
class MyRule(Rule):
    meta = RuleMeta(
        id="AI-LOGIC-005",
        name="Rule name",
        description="What it catches",
        severity=Severity.WARNING,
        multiplier="1.75x",
        source="Research citation",
    )

    def check(self, root, source, file_path):
        findings = []
        for node in self.find_all(root, "some_node_type"):
            if <condition>:
                findings.append(self._make_finding(
                    file_path, node, source,
                    message="What went wrong",
                    fix="How to fix it",
                ))
        return findings
```

Then add the import to `src/astray/rules/registry.py` and add a test fixture in `tests/fixtures/`.

---

## Research

- [CodeRabbit: AI vs Human Code Report (Dec 2025)](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report)
- [Survey of Bugs in AI-Generated Code (Dec 2025)](https://arxiv.org/html/2512.05239v1)
- [CMU Security Benchmark](https://dev.to/solobillions/i-tested-every-vibe-coding-security-scanner-2026-heres-what-actually-works-p9k)
- [eslint-plugin-llm-core](https://dev.to/pertrai1/i-analyzed-500-ai-coding-mistakes-and-built-an-eslint-plugin-to-catch-them-jme)
- [AI Tech Debt: 110K+ issues](https://arxiv.org/html/2603.28592)

---

## License

MIT
