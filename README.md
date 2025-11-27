# From Demo to Production: A Guide to Shipping Claude in Your Organization

> For the developer who saw Claude do something impressive and is now asking: "How do I make this real for my team?"

---

## The Story

I went to the AI Engineer Code Summit in NYC (November 2025), hosted by Swyx. Talk after talk covered reinforcement learning, synchronous vs. asynchronous approaches, LLM observability, evaluations. The depth was overwhelming—in the best way.

Then I attended a workshop with Thariq Shihipar from the Claude Agent SDK team at Anthropic. He was generous with his time, walking through the migration path from the v1 Messages API into adopting the broader Claude ecosystem.

That conversation clarified something I'd been struggling with:

**The gap isn't capability. It's the journey.**

How do you go from "I tried Claude and it worked" to "we're shipping Claude in production with confidence"?

This guide is that journey.

---

## Who This Is For

Someone at your company saw a demo. Maybe Claude with Excel. Maybe Claude with PowerPoint. Maybe something custom that blew their mind.

They tried it in the Claude UI at [claude.ai](https://claude.ai). It worked.

Now they're back asking: *"Can we replicate this? Can we scale it?"*

You don't know where to start. You might not even know that the Claude Console exists, or how it's different from the API, or what "evals" means in this context.

**By the end of this guide, you'll know:**

1. The Anthropic landscape—which tool to use when
2. How to validate your prompt works reliably before shipping
3. How to run automated checks so you don't break things in production
4. What "good enough" looks like at each stage

---

## Quick Start

For those who want to try it now:

```bash
# Clone and setup
git clone <this-repo>
cd claude-production-pipeline
pip install -r requirements.txt

# Preview what tests will run (no API key needed)
python eval_runner.py --dry-run

# When ready, set your API key (get one at console.anthropic.com)
export ANTHROPIC_API_KEY=your-key-here

# Run the evals for real
python eval_runner.py
```

Expected output:
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

Now read on to understand *why* this matters.

---

## The Landscape: Five Ways to Access Claude

It's easy to get lost. Here's the map:

| Tool | What It Is | When to Use It |
|------|-----------|----------------|
| **Claude UI** (claude.ai) | The chat product | Exploration, personal use, showing what's possible |
| **Claude Console** | The workbench for developers | Building prompts, testing with golden datasets, iteration |
| **Claude API** | The integration point | Shipping to production, embedding in your product |
| **Claude Agent SDK** | The agentic harness | Building autonomous agents that use tools, files, code execution |
| **Claude Code** | Anthropic's coding agent | Developer productivity, agentic coding in your terminal |

**The key insight:** 

- Claude UI is where you *discover* what's possible
- Console is where you *validate* that it works reliably  
- API is where you *ship* it to your users
- Agent SDK is where you *build* autonomous workflows
- Claude Code is where you *accelerate* your own development

Most teams get stuck between Console and API. That's the bridge we're building here.

---

## The Journey: Four Stages

### Stage 1: Capture What Worked

You have a prompt that worked in the Claude UI. Before anything else, write it down.

**Identify the variables**—the parts that change between uses:

```
You are a customer support assistant for {{COMPANY_NAME}}.

The customer's question is:
{{CUSTOMER_QUESTION}}

The relevant documentation is:
{{DOCUMENTATION}}

Provide a helpful, accurate response.
```

The pieces in `{{DOUBLE_BRACES}}` are your variables. Everything else is your prompt template.

**Action:** Create a file called `prompt.txt` with your template.

---

### Stage 2: Validate in Console

The [Claude Console](https://console.anthropic.com) is where you build confidence that your prompt works reliably—not just once, but across many inputs.

**Why this matters:** A prompt that works on one example might fail on edge cases. Console lets you test systematically before you ship.

**Steps:**

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create a new prompt with your template
3. Add test cases—inputs and what you expect the output to look like
4. Run all tests. See what passes, what fails.
5. Iterate until you trust it.

**How many test cases?** Start with 5-10. Cover:
- 2-3 "happy path" cases (typical inputs)
- 2-3 edge cases (unusual inputs, empty fields, very long inputs)
- 2-3 failure modes (inputs that should trigger specific behavior)

**Pro tip:** You can import test cases from a CSV file. Structure your golden dataset outside Console, import it, iterate in Console, then use the same dataset for automated testing.

---

### Stage 3: Ship via API

Once you trust your prompt, ship it via the API.

**The mental model:** Your prompt template + the API = your production system.

```python
import anthropic

client = anthropic.Anthropic()

def get_support_response(company_name: str, question: str, docs: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user", 
                "content": f"""You are a customer support assistant for {company_name}.

The customer's question is:
{question}

The relevant documentation is:
{docs}

Provide a helpful, accurate response."""
            }
        ]
    )
    return message.content[0].text
```

**That's it.** The same prompt you validated in Console, now callable from your code.

---

### Stage 4: Maintain Confidence with Evals

Here's where most teams skip—and regret it later.

You validated your prompt once. But prompts change. Models update. Edge cases emerge. How do you know it still works after the 47th tweak?

**Evals are your regression tests.**

The same golden dataset you used in Console becomes your automated test suite:

```python
# eval_runner.py
import csv
import anthropic
import sys

client = anthropic.Anthropic()

def run_eval(dataset_path: str, prompt_template: str) -> tuple[int, int]:
    """Run evals, return (passed, total)"""
    passed = 0
    total = 0
    
    with open(dataset_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            
            # Fill in the template
            prompt = prompt_template
            for key, value in row.items():
                if key != 'expected_output':
                    prompt = prompt.replace(f"{{{{{key}}}}}", value)
            
            # Call the API
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            actual = response.content[0].text
            expected = row['expected_output']
            
            # Simple check: does the response contain what we expect?
            if expected.lower() in actual.lower():
                passed += 1
                print(f"✓ Test {total}: PASSED")
            else:
                print(f"✗ Test {total}: FAILED")
                print(f"  Expected to contain: {expected}")
                print(f"  Got: {actual[:200]}...")
    
    return passed, total

if __name__ == "__main__":
    with open("prompt.txt") as f:
        template = f.read()
    
    passed, total = run_eval("golden_dataset.csv", template)
    print(f"\n{passed}/{total} tests passed")
    
    if passed < total:
        sys.exit(1)  # Fail CI if any tests fail
```

**Your golden dataset** (`golden_dataset.csv`):

```csv
COMPANY_NAME,CUSTOMER_QUESTION,DOCUMENTATION,expected_output
Acme Inc,How do I reset my password?,Users can reset passwords at acme.com/reset,acme.com/reset
Acme Inc,What are your hours?,We are open Monday-Friday 9am-5pm,Monday-Friday
Acme Inc,Do you offer refunds?,Full refunds within 30 days of purchase,30 days
Acme Inc,,No documentation available,I don't have enough information
Acme Inc,Tell me about your competitor's product,We sell widgets and gadgets,I can only help with Acme
```

**Wire it into CI** (`.github/workflows/eval.yml`):

```yaml
name: Prompt Evals

on:
  pull_request:
    paths:
      - 'prompt.txt'
      - 'golden_dataset.csv'

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install anthropic
      
      - name: Run evals
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python eval_runner.py
```

**Now every PR that touches your prompt runs your test suite.** Bad changes get caught before they ship.

---

## The Checklist: You're Ready When...

- [ ] You can explain the difference between Console and API
- [ ] You have a prompt template in version control
- [ ] You have a golden dataset with at least 5 test cases
- [ ] You've run evals locally and seen them pass/fail
- [ ] You've added the CI gate (or know how to)

If you've checked all five, you've crossed the bridge. You're shipping Claude in production with confidence.

---

## Common Mistakes

**Starting with too many test cases.** Five good tests beat fifty mediocre ones. Start small, add tests when you find bugs.

**Over-engineering the eval.** "Does the output contain the expected substring?" is a perfectly valid eval. You don't need LLM-as-judge on day one.

**Skipping Console.** It's tempting to jump straight to code. Don't. Console builds intuition. You'll catch problems faster with the visual interface.

**Not versioning your prompt.** Your prompt is code. Treat it like code. Put it in git.

---

## What's Next

This guide covers **Level 1 evals**—simple, deterministic checks. They'll get you far.

When you're ready to level up:

- **LLM-as-Judge:** For subjective quality ("Is this response helpful?"), use Claude to grade Claude. [Hamel Husain's guide](https://hamel.dev/blog/posts/llm-judge/) is the definitive resource.

- **Observability:** For production debugging and monitoring, explore [Anthropic's documentation on logging and tracing](https://docs.anthropic.com).

- **Agent SDK:** For autonomous workflows that go beyond single API calls, check out the [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code/sdk). Thariq's post on [building agents](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) is the starting point.

---

## The Files

This repo contains everything you need:

```
├── README.md              # This guide
├── PRD.md                 # Problem Requirements Document (for PMs)
├── RFC.md                 # Technical Design Document (for Tech Leads)
├── requirements.txt       # Python dependencies
├── prompt.txt             # Example prompt template
├── golden_dataset.csv     # Example test cases
├── eval_runner.py         # Eval script
└── .github/
    └── workflows/
        └── eval.yml       # CI configuration
```

Clone it. Replace the example prompt with yours. Add your test cases. Ship with confidence.

---

## For Tech Leads

See **[RFC.md](./RFC.md)** for the technical design document covering:
- Architecture decisions and rationale
- Why we chose CSV over JSON, substring matching over LLM-as-judge
- Abandoned ideas and why they were rejected
- Implementation phases and security considerations

The RFC follows [HashiCorp's RFC template](https://works.hashicorp.com/articles/rfc-template).

---

## For PMs

See **[PRD.md](./PRD.md)** for the problem requirements document covering:
- Problem statements with user personas
- Evidence and success metrics
- Phased requirements for iterative delivery
- The "why" behind this starter kit

The PRD follows [HashiCorp's PRD template](https://works.hashicorp.com/articles/prd-template).

---

## Credits

This guide was shaped by conversations at the AI Engineer Code Summit (NYC, November 2025) and Thariq Shihipar's generous workshop on the Claude ecosystem.

The eval philosophy draws heavily from [Hamel Husain's work on LLM evaluations](https://hamel.dev/blog/posts/evals/)—if you want to go deeper, start there.

For the broader context on how AI engineering is evolving, follow [Swyx's Latent Space](https://www.latent.space/) podcast and newsletter.

---

*Built for the developer who saw the demo and wants to make it real.*
