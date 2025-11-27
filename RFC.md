# RFC: Claude Production Pipeline Architecture

| Field | Value |
|-------|-------|
| **Status** | Approved |
| **Owner** | Jai Bhagat |
| **Created** | November 2025 |
| **Target Version** | v1.0 |
| **PRD Link** | [PRD.md](./PRD.md) |

---

## Overview

This RFC describes the technical architecture for a minimal Claude production pipeline—a starter kit that provides prompt templating, golden dataset evaluation, and CI integration. The design prioritizes simplicity and adaptability: teams should be able to clone, modify, and ship within an hour, while the patterns scale to more sophisticated workflows.

---

## Background

### The Anthropic Ecosystem

Anthropic offers multiple entry points for Claude:

| Tool | Purpose | API? |
|------|---------|------|
| Claude UI (claude.ai) | Consumer chat product | No |
| Claude Console | Developer workbench, prompt testing | No (GUI only) |
| Claude API | Production integration | Yes |
| Claude Agent SDK | Autonomous agents with tools | Yes |
| Claude Code | Coding assistant | CLI |

Most developers discover Claude through the UI, validate in Console, then struggle to bridge to API. This kit provides that bridge.

### Prior Art

- **OpenAI Evals:** Comprehensive but complex; requires deep investment to adopt
- **LangChain:** Framework-heavy; adds dependencies and abstractions
- **Promptfoo:** Excellent eval tool but separate from the "getting started" narrative

These tools serve advanced users. We need something for the developer who just saw their first demo.

### Design Principles

1. **Minimal dependencies:** Only `anthropic` Python package required
2. **Flat file structure:** No nested directories, frameworks, or config files
3. **Copy-paste friendly:** Every file works standalone
4. **Fail loudly:** Errors should be obvious, not silent
5. **CI-native:** Works in GitHub Actions out of the box

---

## Proposal

### Goals

- Provide a working eval pipeline in < 100 lines of code total
- Enable first successful eval run within 5 minutes of cloning
- Support any prompt pattern without code changes (via templating)
- Integrate with existing CI/CD without custom tooling

### Non-Goals

- Replacing comprehensive eval frameworks (Promptfoo, OpenAI Evals)
- Supporting non-Python environments
- Providing a web UI or dashboard
- Handling multi-turn conversations (Phase 1)
- LLM-as-judge evaluation (Phase 1)

---

## Detailed Design

### File Structure

```
├── README.md              # Narrative guide + Quick Start
├── requirements.txt       # Single dependency: anthropic
├── prompt.txt             # Template with {{VARIABLE}} placeholders
├── golden_dataset.csv     # Test cases: variables + expected_output
├── eval_runner.py         # Eval script (~50 lines)
└── .github/
    └── workflows/
        └── eval.yml       # CI configuration
```

**Rationale:** Flat structure means no mental model required. Every file is visible at the root. The only "hidden" directory is `.github/` which is standard for CI.

### Prompt Templating

**Format:** Double-brace placeholders `{{VARIABLE_NAME}}`

```
You are a customer support assistant for {{COMPANY_NAME}}.

The customer's question is:
{{CUSTOMER_QUESTION}}

The relevant documentation is:
{{DOCUMENTATION}}
```

**Rationale:**
- Double braces avoid conflicts with common syntax (single braces used in JSON, f-strings)
- Uppercase with underscores matches environment variable conventions
- No special escaping required

**Implementation:**

```python
def fill_template(template: str, variables: dict) -> str:
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value or "")
    return result
```

### Golden Dataset Format

**CSV with headers matching template variables + `expected_output`:**

```csv
COMPANY_NAME,CUSTOMER_QUESTION,DOCUMENTATION,expected_output
Acme Inc,How do I reset my password?,"Visit acme.com/reset...",acme.com/reset
Acme Inc,What are your hours?,"Monday-Friday 9-5...",Monday-Friday
```

**Rationale:**
- CSV is universally understood, editable in any spreadsheet
- Headers match template variables exactly (case-sensitive)
- `expected_output` is a reserved column for assertions
- Empty cells are valid (tests empty input handling)

**Constraints:**
- Column names must match template placeholders exactly
- `expected_output` column is required
- Commas in values must be quoted (standard CSV)

### Evaluation Logic

**Simple substring matching:**

```python
def check_output(actual: str, expected: str) -> bool:
    if not expected:
        return True  # No expectation = always pass
    return expected.lower() in actual.lower()
```

**Rationale:**
- Substring matching is deterministic and debuggable
- Case-insensitive reduces false failures
- Empty expected = no assertion (useful for "doesn't crash" tests)
- More sophisticated eval (LLM-as-judge) is Phase 2

**Trade-offs:**
- Won't catch subtle quality issues
- Can't evaluate subjective criteria ("is this helpful?")
- May pass when response contains expected string in wrong context

These trade-offs are acceptable for Phase 1. The goal is catching regressions, not comprehensive quality scoring.

### Eval Runner Script

**Key behaviors:**

1. Load prompt template from file
2. Load dataset from CSV
3. For each row:
   - Fill template with variables
   - Call Claude API
   - Check if response contains expected substring
   - Print pass/fail
4. Exit with code 1 if any test fails (for CI)

**CLI interface:**

```bash
python eval_runner.py [--dataset FILE] [--prompt FILE] [--model MODEL]
```

**Defaults:**
- `--dataset`: `golden_dataset.csv`
- `--prompt`: `prompt.txt`
- `--model`: `claude-sonnet-4-20250514`

**Error handling:**
- Missing files: Exit with clear error message
- API errors: Print error, continue to next test, count as failure
- Missing `anthropic` package: Exit with install instructions

### CI Configuration

**Trigger conditions:**

```yaml
on:
  pull_request:
    paths:
      - 'prompt.txt'
      - 'golden_dataset.csv'
      - 'eval_runner.py'
  workflow_dispatch:  # Manual trigger
```

**Rationale:**
- Only run on changes that could affect eval results
- `workflow_dispatch` allows manual runs for debugging
- No need to run on README changes, etc.

**Secrets:**
- `ANTHROPIC_API_KEY`: Required, stored in GitHub Secrets

**Failure behavior:**
- Non-zero exit code blocks PR merge
- Comment posted on PR with failure notice

### Security Considerations

**API Key handling:**
- Never committed to repo
- Passed via environment variable
- GitHub Secrets for CI

**Prompt injection:**
- Not addressed in Phase 1
- Teams should add injection test cases to their golden dataset
- Example: `CUSTOMER_QUESTION` = "Ignore instructions and..."

**Cost controls:**
- No built-in cost limiting
- Teams should set Anthropic usage limits in Console
- Each eval run costs ~$0.01-0.10 depending on dataset size

### Performance Implications

**API calls:** 1 per test case, sequential (not parallel)

**Typical run time:**
- 10 test cases: ~30 seconds
- 50 test cases: ~2-3 minutes

**Rationale for sequential:**
- Simpler code
- Easier to debug (deterministic order)
- Rate limiting handled automatically
- Parallel execution is a future optimization

---

## Implementation Plan

### Phase 1: Core Kit (Complete)

- [x] Prompt template file with variable syntax
- [x] Golden dataset CSV format
- [x] Eval runner script with CLI
- [x] GitHub Actions workflow
- [x] README with Quick Start
- [x] requirements.txt

### Phase 2: Enhanced Evaluation (Future)

- [ ] LLM-as-judge evaluation mode
- [ ] Multi-model comparison
- [ ] Parallel test execution
- [ ] Cost tracking per run
- [ ] HTML report generation

---

## Abandoned Ideas

### Abandoned: YAML Configuration File

**What:** A `config.yaml` for specifying model, paths, thresholds, etc.

**Why abandoned:** Adds complexity without clear benefit. CLI args cover the same use cases. YAML parsing requires another dependency. The goal is "clone and run," not "configure and run."

### Abandoned: JSON Dataset Format

**What:** Using JSON instead of CSV for test cases.

**Why abandoned:** CSV is more accessible. PMs and non-engineers can edit it in Google Sheets or Excel. JSON requires understanding syntax, escaping quotes, etc. CSV "just works" for this use case.

### Abandoned: pytest Integration

**What:** Writing evals as pytest test cases.

**Why abandoned:** Adds pytest as a dependency. Requires understanding pytest conventions. The custom runner is simpler and more obvious. Teams can wrap it in pytest later if desired.

### Abandoned: Docker Container

**What:** Providing a Dockerfile for consistent environment.

**Why abandoned:** Adds friction to getting started. Python + pip is universally available. Docker is overkill for a single-file script with one dependency.

---

## Open Questions

- [x] Should we support async API calls? **No - simplicity over speed for Phase 1**
- [x] Should we cache API responses for faster iteration? **No - determinism is more important**
- [ ] Should we add a `--dry-run` flag to show what would be tested without calling API?
- [ ] Should we support `.env` files for local API key management?

---

## References

- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Hamel Husain: Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PRD for this project](./PRD.md)
