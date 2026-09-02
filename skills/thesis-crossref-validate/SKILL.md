---
name: thesis-crossref-validate
description: Validate citation counts and metadata for a paper via the free CrossRef API. No browser needed. Use when the user needs to check citation counts, verify a DOI, get publication metadata, or assess basic citation health for thesis sources without a Scite account. Works in Claude, Codex, Gemini CLI, or any AI that can fetch a URL or run Python.
---

# Thesis CrossRef Validate

Free citation metadata using the CrossRef API (metadata for 140M+ DOIs, no auth required).

## When to Use This vs thesis-scite-validate

| Situation | Use |
| --- | --- |
| No Scite account / no browser | `thesis-crossref-validate` (this skill) |
| Need supporting vs contrasting citation context | `thesis-scite-validate` (Scite Smart Citations) |
| Running in Codex, Gemini CLI, or any non-Claude agent | `thesis-crossref-validate` |
| Quick DOI verification + citation count | `thesis-crossref-validate` |

Note: CrossRef gives citation counts and metadata. It does NOT distinguish supporting from
contrasting citations — that is Scite's unique feature. For citation-risk decisions in thesis
work, combine CrossRef counts with Semantic Scholar's `influentialCitationCount`.

## Workflow

1. Identify the paper by DOI (preferred), title, or URL.
2. If only a title is available, resolve the DOI first using CrossRef's query endpoint.
3. Choose execution method (see Execution Modes below).
4. Extract: citation count, references list, journal, publisher, license, retraction status.
5. Check Retraction Watch via CrossRef's `is-referenced-by-count` and `update-to` fields.
6. Assign `risk_level` from visible evidence.
7. Before finalizing output, read `references/quality-check.md`.

## Execution Modes

### Mode 1 — Direct API call by DOI (WebFetch / curl)

```
GET https://api.crossref.org/works/DOI
```

Example:
```
GET https://api.crossref.org/works/10.1016/j.ijheh.2020.113629
```

Add `?mailto=YOUR_EMAIL` for the polite pool.

### Mode 2 — Resolve DOI from title

```
GET https://api.crossref.org/works?query.title=TITLE&rows=3&select=DOI,title,author,issued,is-referenced-by-count
```

Pick the best match by title similarity and year.

### Mode 3 — Semantic Scholar (richer citation data)

```
GET https://api.semanticscholar.org/graph/v1/paper/DOI?fields=title,authors,year,citationCount,influentialCitationCount,isOpenAccess,openAccessPdf
```

### Mode 4 — Python script (Codex / Gemini / any bash-capable agent)

```bash
python scripts/api/crossref_validate.py "10.1016/j.ijheh.2020.113629"
```

## Risk Level Rules

| Evidence | `risk_level` |
| --- | --- |
| 0 citations, less than 2 years old | `unknown` |
| 0 citations, older than 3 years | `high` |
| Low citations for field and age | `moderate` |
| `update-to` contains retraction record | `high` |
| High `influentialCitationCount` (Semantic Scholar) | `low` |
| Large citation count, no retraction | `low` |

## Output Contract

Return matching `schemas/crossref-validate.schema.json`:

```json
{
  "platform": "CrossRef",
  "paper": {
    "title": "paper title",
    "authors": [],
    "year": 2020,
    "doi": "10.xxxx/xxxx",
    "url": null,
    "citation_status": {
      "counts_available": true,
      "supporting": null,
      "contrasting": null,
      "mentioning": 42
    },
    "decision": "keep",
    "notes": "citation risk"
  },
  "crossref_metadata": {
    "publisher": "",
    "journal": "",
    "license": null,
    "retracted": false,
    "influential_citations": null
  },
  "citation_context": {
    "risk_level": "low",
    "recommended_use": "cite as background",
    "note": "CrossRef does not distinguish supporting from contrasting citations. Use thesis-scite-validate for Smart Citations."
  }
}
```

## Generic Mode

If no HTTP access, produce a CrossRef lookup checklist and mark all counts as `null`
with `counts_available: false`. Do not invent citation counts.
