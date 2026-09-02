---
name: thesis-openalex-search
description: Search academic papers via the free OpenAlex API for thesis evidence. No browser needed. Use when the user needs peer-reviewed papers, evidence, claims, literature, or research findings for a thesis question without a Consensus account or any browser. Works in Claude, Codex, Gemini CLI, or any AI that can fetch a URL or run Python.
---

# Thesis OpenAlex Search

Free evidence search using the OpenAlex API (250M+ academic works, no auth required).

## When to Use This vs thesis-consensus-search

| Situation | Use |
| --- | --- |
| No Consensus account / no browser | `thesis-openalex-search` (this skill) |
| Want Consensus AI synthesis + UI | `thesis-consensus-search` |
| Running in Codex, Gemini CLI, or any non-Claude agent | `thesis-openalex-search` |
| Fastest first pass on any machine | `thesis-openalex-search` |

## Workflow

1. Parse the research question into 3–5 searchable terms (English preferred — OpenAlex indexes in English).
2. Choose execution method based on available tools (see Execution Modes below).
3. Query OpenAlex. Apply filters: `publication_year`, `type:article`, `is_oa` if open access is preferred.
4. Sort by `cited_by_count:desc` for established evidence; by `publication_date:desc` for recent work.
5. Normalize results into evidence cards. Reconstruct abstracts from `abstract_inverted_index`.
6. Mark each paper `keep`, `maybe`, or `reject`.
7. Send `keep` papers to `thesis-crossref-validate` or `thesis-scite-validate` for citation risk.
8. Before finalizing output, read `references/quality-check.md`.

## Execution Modes

### Mode 1 — Direct API call (WebFetch / curl)

Any agent with HTTP fetch capability:

```
GET https://api.openalex.org/works?search=QUERY&filter=type:article,publication_year:>2015&sort=cited_by_count:desc&per-page=20&select=id,doi,title,authorships,publication_year,abstract_inverted_index,cited_by_count,concepts,open_access&mailto=user@email.com
```

Replace `QUERY` with URL-encoded search terms. Add `&mailto=YOUR_EMAIL` for the polite pool (higher rate limits, no auth needed).

### Mode 2 — Python script (Codex / Gemini / any bash-capable agent)

```bash
python scripts/api/openalex_search.py "cognitive load theory online learning"
```

Returns JSON matching `schemas/openalex-search.schema.json`.

### Mode 3 — Chrome MCP (Claude Code only)

Navigate to `https://openalex.org/works?search=QUERY` and extract results from the page.

## API Response Fields

| OpenAlex field | Maps to paper field |
| --- | --- |
| `title` | `title` |
| `authorships[].author.display_name` | `authors[]` |
| `publication_year` | `year` |
| `doi` (remove `https://doi.org/` prefix) | `doi` |
| `id` (OpenAlex URL) | `url` |
| `abstract_inverted_index` | `abstract` (reconstruct) |
| `cited_by_count` | `citation_status.mentioning` (approximate) |
| `concepts[].display_name` | use to assess relevance |
| `open_access.oa_url` | free PDF URL when available |

### Reconstruct abstract from inverted index

```python
def reconstruct_abstract(inverted_index: dict) -> str:
    if not inverted_index:
        return ""
    positions = {pos: word for word, positions in inverted_index.items() for pos in positions}
    return " ".join(positions[i] for i in sorted(positions))
```

## Output Contract

Return matching `schemas/openalex-search.schema.json`:

```json
{
  "query": "focused research question",
  "platform": "OpenAlex",
  "api_url": "https://api.openalex.org/works?search=...",
  "summary": "one paragraph evidence synthesis",
  "papers": [
    {
      "title": "paper title",
      "authors": [],
      "year": 2024,
      "doi": "10.xxxx/xxxx",
      "url": "https://openalex.org/W...",
      "abstract": "reconstructed abstract",
      "claims": [],
      "methods": [],
      "limitations": [],
      "cited_by_count": 0,
      "open_access_url": null,
      "decision": "keep",
      "notes": "how this helps the thesis"
    }
  ],
  "gaps": [],
  "total_results": 0
}
```

## Generic Mode

If no HTTP access and no Python available, produce:
- search URLs to paste into a browser
- inclusion/exclusion criteria
- extraction table template

Label it as a search plan, not live OpenAlex results.

## Skill Forge Upgrade

After validating the API response shape for your thesis topic, update
`references/quality-check.md` with topic-specific concept filters and
preferred OpenAlex filter combinations.
