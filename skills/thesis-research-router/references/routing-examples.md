# Routing Examples

## Single-platform requests

- "What evidence exists for X?" → try `thesis-consensus-search`, fall back to `thesis-openalex-search`
- "Explain this DOI for my thesis." → try `thesis-scispace-explain`, fall back to explain from abstract
- "Is this paper safe to cite?" → try `thesis-scite-validate`, fall back to `thesis-crossref-validate`
- "Find related authors and papers." → try `thesis-researchrabbit-expand`, fall back to `thesis-openalex-expand`
- "Turn these accepted papers into a paragraph." → try `thesis-jenni-draft`, fall back to draft with Claude

## Full pipeline requests

- "Build a full literature review workflow." → chain: evidence → validate → expand → explain → draft
  - Tier 1 (API only): openalex-search → crossref-validate → openalex-expand → explain from abstract → draft with Claude
  - Tier 3+ (browser): consensus-search → scite-validate → researchrabbit-expand → scispace-explain → jenni-draft

## Fallback transitions (log these in pipeline_executed)

| Primary blocked | Fallback invoked | Reason logged |
| --- | --- | --- |
| `thesis-consensus-search` | `thesis-openalex-search` | "Consensus blocked or no browser" |
| `thesis-scite-validate` | `thesis-crossref-validate` | "Scite paywall or no browser" |
| `thesis-researchrabbit-expand` | `thesis-openalex-expand` | "ResearchRabbit login required" |
| `thesis-scispace-explain` | explain from abstract | "SciSpace login required" |
| `thesis-jenni-draft` | draft with Claude | "Jenni login required" |

## No-browser generic routing (Codex, Gemini CLI)

All platform skills blocked → use full Tier 1 pipeline:
1. `python scripts/api/openalex_search.py "question" --email YOUR_EMAIL`
2. `python scripts/api/crossref_validate.py DOI --semantic` for each keep paper
3. `python scripts/api/openalex_expand.py DOI --direction both` for seed papers
4. Explain papers from abstracts returned by OpenAlex
5. Draft sections from accepted evidence cards using Claude/Codex/Gemini directly
