# PRD: Claude Production Pipeline Starter Kit

| Field | Value |
|-------|-------|
| **Status** | Approved |
| **Owner** | Jai Bhagat |
| **Created** | November 2025 |
| **Target Release** | v1.0 |
| **Engineering Lead** | Katelyn Lesse |
| **Design Lead** | Joel Lewenstein |

---

## Introduction

This PRD defines the requirements for a starter kit that helps developers go from "Claude worked in a demo" to "Claude is running in production with confidence." The kit provides a minimal, opinionated path through the Claude ecosystem—prompt templates, golden datasets, eval scripts, and CI configuration—so teams can ship Claude-powered features without getting lost in tooling decisions.

---

## Background

### The Current State

Developers encounter Claude through demos, workshops, or the Claude UI at claude.ai. They see impressive capabilities and want to bring them to their teams. However:

- The Anthropic ecosystem has multiple entry points (Claude UI, Console, API, Agent SDK, Claude Code) with unclear boundaries
- Most tutorials jump straight to code without explaining validation workflows
- Teams ship prompts without regression testing, then break things silently
- There's no canonical "starter project" showing the demo→production path

### Why This Matters Now

- AI Engineer Summit (Nov 2025) revealed widespread confusion about Console vs. API vs. SDK
- Teams are adopting Claude rapidly but without quality gates
- Support tickets spike after prompt changes because there's no eval safety net
- Competitors (OpenAI, Google) have clearer "getting started" narratives

### Visual: The Gap

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/4e8238cf-2cf5-4d32-bfd4-85cf370bdf97" />

The "???" is what this kit solves.

---

## Problem Statement

### Primary Problem

**As a** developer who saw Claude do something impressive, **I struggle to** turn that demo into a production-ready feature **because** I don't know which Anthropic tools to use when, how to validate my prompt works reliably, or how to prevent regressions, **which results in** either not shipping at all or shipping something fragile that breaks silently.

### Secondary Problems

1. **As a** tech lead, **I struggle to** evaluate whether my team's Claude integration is production-ready **because** there's no standard for "good enough" quality gates.

2. **As a** PM who codes, **I struggle to** prototype Claude features **because** I don't know the minimal viable setup that won't embarrass me when I hand it to engineering.

3. **As a** new team member, **I struggle to** understand how our Claude prompts are tested **because** there's no documented pattern to follow.

### Evidence

| Signal | Source | Volume |
|--------|--------|--------|
| "How do I go from Console to API?" | AI Engineer Summit workshop | 15+ questions in 1hr |
| Prompt regressions in production | Internal post-mortems | 3 incidents in 6 months |
| "What's the difference between claude.ai and Console?" | Developer Slack channels | Weekly occurrence |
| Teams skipping eval entirely | Engineering surveys | 60% of Claude integrations |

---

## Personas

### The Curious Developer

**Who:** Mid-level developer who attended a Claude demo or workshop and wants to build something.

**Goals:** Ship a Claude-powered feature that works reliably without becoming an AI/ML expert.

**Pain points:**
- Overwhelmed by ecosystem options
- Doesn't know what "production-ready" means for LLM features
- Worried about looking foolish with a fragile implementation

**How this affects them:** Spends weeks researching instead of building, or ships something brittle.

### The Skeptical Tech Lead

**Who:** Senior engineer responsible for code quality and system reliability.

**Goals:** Ensure Claude integrations meet the same quality bar as other production code.

**Pain points:**
- No obvious way to review LLM prompts
- No regression tests for prompt changes
- Unclear how to set up CI for Claude features

**How this affects them:** Either blocks Claude adoption or approves PRs they can't properly evaluate.

### The Vibe-Coding PM

**Who:** Product manager who prototypes features in code before handing off to engineering.

**Goals:** Build a working prototype that demonstrates feasibility without embarrassing technical debt.

**Pain points:**
- Doesn't know the "right" way to structure Claude code
- Prototypes work locally but don't translate to production
- Wants to hand off something engineers respect

**How this affects them:** Prototypes get rewritten from scratch, wasting effort and creating friction.

---

## Success Criteria

### Metrics

| Metric | Current | Target | How Measured |
|--------|---------|--------|--------------|
| Time from "saw demo" to "running in CI" | Unknown (weeks?) | < 1 hour | User feedback |
| Teams with eval coverage for Claude prompts | ~40% | 80% | Engineering survey |
| Prompt regression incidents | 3/6 months | 0 | Incident tracking |
| README comprehension | — | 90% can run eval in 5 min | User testing |

### Qualitative Signals

- Tech leads say "I finally understand the Anthropic ecosystem"
- PMs successfully prototype without engineering rewrite
- New team members onboard to Claude patterns in < 1 day
- Teams proactively add test cases when they find edge cases

---

## Phased Requirements

### Phase 1: Minimum Viable Starter Kit

**Objective:** Enable any developer to go from zero to running evals in CI within 1 hour.

**Requirements:**

- **Prompt template file:** A `.txt` file with `{{VARIABLE}}` placeholders that demonstrates the pattern
  - Acceptance criteria: Can be copied and modified for any use case

- **Golden dataset:** A `.csv` file with input variables and expected outputs
  - Acceptance criteria: 5-10 diverse test cases covering happy path, edge cases, and failure modes

- **Eval runner script:** A Python script (~50 lines) that runs the dataset against the API
  - Acceptance criteria: Clear pass/fail output, exits with code 1 on failure

- **CI configuration:** GitHub Actions workflow that runs evals on PR
  - Acceptance criteria: Triggers on prompt/dataset changes, blocks merge on failure

- **README guide:** Explains the journey from demo to production
  - Acceptance criteria: New user can run eval locally in < 5 minutes with Quick Start

**Out of scope for Phase 1:**
- LLM-as-judge evaluation
- Multiple prompt variants
- Cost tracking
- Observability/logging

---

### Phase 2: Enhanced Evaluation (Future)

**Objective:** Support more sophisticated eval patterns for teams with mature needs.

**Requirements:**

- **LLM-as-judge option:** Use Claude to evaluate Claude outputs for subjective quality
  - Acceptance criteria: Configurable rubric, clear scoring output

- **Multi-model comparison:** Run same prompts against different models
  - Acceptance criteria: Side-by-side results, cost comparison

- **Eval dashboard:** Visual history of eval runs over time
  - Acceptance criteria: Trend lines, regression detection

**Out of scope for Phase 2:**
- Fine-tuning workflows
- RAG pipeline integration
- Multi-turn conversation testing

---

## User Experience

### User Flow: First-Time Setup

1. Developer clones the repo
2. Developer reads README Quick Start section
3. Developer runs `pip install -r requirements.txt`
4. Developer sets `ANTHROPIC_API_KEY`
5. Developer runs `python eval_runner.py`
6. Developer sees pass/fail output
7. Developer modifies `prompt.txt` with their prompt
8. Developer modifies `golden_dataset.csv` with their test cases
9. Developer runs eval again to validate
10. Developer pushes to GitHub, CI runs automatically

### Expected Terminal Output

```
Running evals...
  Dataset: golden_dataset.csv
  Prompt:  prompt.txt
  Model:   claude-sonnet-4-20250514
----------------------------------------
✓ Test 1: PASSED
✓ Test 2: PASSED
✓ Test 3: PASSED
...
----------------------------------------
Results: 10/10 tests passed (100%)

All tests passed!
```

---

## Open Questions

- [x] Should we include a `requirements.txt`? **Yes - added**
- [x] Should the README be narrative or reference-style? **Narrative with Quick Start**
- [ ] Should we provide multiple example prompts for different use cases?
- [ ] Should we include a Makefile for common commands?

---

## References

- [Hamel Husain: LLM Evaluations](https://hamel.dev/blog/posts/evals/)
- [Anthropic Console Documentation](https://console.anthropic.com)
- [AI Engineer Summit NYC, November 2025](https://www.ai.engineer/)
