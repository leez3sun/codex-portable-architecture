---
name: thesis-research-router
description: Route and orchestrate thesis research tasks across all 9 skills. Detects available tools, selects the best skill tier, and falls back to free API skills when platform skills are blocked. Use when the user asks what platform to use, wants a research plan, full thesis workflow, or any broad academic task that needs evidence search, citation validation, literature expansion, paper explanation, or drafting.
---

# Thesis Research Router

Orchestrate all 9 thesis research skills. Detect what works, use the best tier, fall back automatically.

## Skill Inventory

**Free API skills (Tier 1 — always available):**
- `thesis-openalex-search` — evidence search via OpenAlex API
- `thesis-crossref-validate` — citation count + risk via CrossRef
- `thesis-openalex-expand` — literature expansion via OpenAlex citation graph

**Platform skills (Tier 2–4 — need browser or account):**
- `thesis-consensus-search` — Consensus evidence search (public, browser needed)
- `thesis-scite-validate` — Scite Smart Citations (partial public, browser needed)
- `thesis-researchrabbit-expand` — ResearchRabbit literature map (login required)
- `thesis-scispace-explain` — SciSpace paper explanation (login required)
- `thesis-jenni-draft` — Jenni academic drafting (login required)

## Tier Detection

Run this check before the first skill invocation:

| Check | Tier available |
| --- | --- |
| Can make HTTP requests or run Python scripts | Tier 1 (API) ✓ |
| `playwright --version` returns a version | Tier 2 (Playwright) ✓ |
| `mcp__Claude_in_Chrome__navigate` tool is available | Tier 3 (Chrome MCP) ✓ |
| `browser-act --version` returns a version | Tier 4 (BrowserAct) ✓ |

Default to **Tier 1** for all tasks. Upgrade to a higher tier only when the user specifically wants the platform experience (Consensus AI synthesis, Scite Smart Citations, ResearchRabbit visual maps).

## Routing Table

| User intent | Try first | Fall back to |
| --- | --- | --- |
| "Find evidence papers" | `thesis-consensus-search` (if browser available) | `thesis-openalex-search` |
| "Validate this citation" | `thesis-scite-validate` (if browser + partial access) | `thesis-crossref-validate` |
| "Find related papers" | `thesis-researchrabbit-expand` (if login available) | `thesis-openalex-expand` |
| "Explain this paper" | `thesis-scispace-explain` (if login available) | explain from abstract (Claude) |
| "Draft this section" | `thesis-jenni-draft` (if login available) | draft from evidence cards (Claude) |
| "Full thesis pipeline" | chain all — see pipelines below | use API tier for blocked steps |

## Fallback Rules

A skill is **blocked** when it reports: login required, CAPTCHA, paywall, browser unavailable,
or generic mode triggered. When a skill is blocked, apply these fallbacks immediately:

```
thesis-consensus-search blocked     → invoke thesis-openalex-search (same query)
thesis-scite-validate blocked       → invoke thesis-crossref-validate (same DOI)
thesis-researchrabbit-expand blocked → invoke thesis-openalex-expand (same seed DOIs)
thesis-scispace-explain blocked     → explain paper from abstract using Claude directly
thesis-jenni-draft blocked          → draft from evidence cards using Claude directly
```

Always report to the user which tier was used and why.

## Orchestration

Invoke skills using the Skill tool. Pass output of each step as input to the next.

### Single-Platform Request

```
Skill(skill="thesis-consensus-search", args="<user research question>")
# If blocked:
Skill(skill="thesis-openalex-search", args="<same query>")
```

### Evidence Pipeline (most common)

```
Step 1: Skill(skill="thesis-consensus-search" OR "thesis-openalex-search", args="<question>")
        → returns evidence cards with keep/maybe/reject decisions

Step 2: For each keep paper with DOI:
        Skill(skill="thesis-scite-validate" OR "thesis-crossref-validate", args="<DOI>")
        → updates citation_status and risk_level on each paper

Step 3: For strongest keep papers:
        Skill(skill="thesis-scispace-explain", args="<DOI or title>")
        OR explain from abstract directly if SciSpace is blocked
```

### Full Thesis Pipeline

```
Step 1: Evidence search (consensus or openalex)
Step 2: Citation validation (scite or crossref) for all keep papers
Step 3: Literature expansion (researchrabbit or openalex) from kept seeds
Step 4: Paper explanation (scispace or Claude) for top papers
Step 5: Section draft (jenni or Claude) from accepted evidence cards
```

### Writing Pipeline

```
Step 1: Confirm accepted evidence cards exist in thesis memory
Step 2: Skill(skill="thesis-jenni-draft", args="<section> + <evidence JSON>")
        OR draft from evidence cards using Claude if Jenni is blocked
```

## Orchestration Rules

1. Classify user intent before invoking any skill.
2. Always try Tier 1 (API) first for evidence and citation tasks unless the user asks for the platform specifically.
3. If private text, credentials, or paid-platform actions appear, pause and ask before proceeding.
4. After each skill, check for blockers. Apply fallback immediately — do not ask the user unless the fallback also fails.
5. Preserve paper fields across all steps: title, authors, year, DOI, URL, claims, methods, limitations, citation_status, decision, notes.
6. Update thesis memory after each step: move papers to `accepted_papers`, `maybe_papers`, or `rejected_papers`.
7. If both primary and fallback fail, report the gap and continue with the remaining pipeline steps.
8. Before finalizing output, read `references/routing-examples.md`.

## Output

After all steps complete, return:

```json
{
  "intent": "full evidence pipeline",
  "tiers_used": ["Tier 1 API", "Tier 3 Chrome MCP"],
  "pipeline_executed": [
    { "skill": "thesis-openalex-search", "status": "completed", "papers_found": 12 },
    { "skill": "thesis-scite-validate", "status": "blocked — fell back to thesis-crossref-validate" },
    { "skill": "thesis-crossref-validate", "status": "completed", "papers_validated": 5 }
  ],
  "handoff_fields": ["title", "authors", "year", "doi", "url", "decision", "notes"],
  "papers_accepted": 0,
  "papers_maybe": 0,
  "papers_rejected": 0,
  "gaps": []
}
```

## Generic Mode

If no tools are available at all (no HTTP, no browser, no Python), produce a step-by-step
research plan. Clearly label every step as requiring manual execution.
See `docs/free-tools.md` for what to run at each step.
