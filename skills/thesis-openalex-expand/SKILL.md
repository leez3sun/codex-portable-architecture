---
name: thesis-openalex-expand
description: Expand thesis literature using the free OpenAlex citation graph. No browser needed. Use when the user needs related papers, forward citations, backward citations, co-cited authors, literature clusters, or snowballing from seed papers without a ResearchRabbit account. Works in Claude, Codex, Gemini CLI, or any AI that can fetch a URL or run Python.
---

# Thesis OpenAlex Expand

Free literature expansion using the OpenAlex citation graph (250M+ works, free API, no auth).

## When to Use This vs thesis-researchrabbit-expand

| Situation | Use |
| --- | --- |
| No ResearchRabbit account / no browser | `thesis-openalex-expand` (this skill) |
| Need visual literature map in ResearchRabbit UI | `thesis-researchrabbit-expand` |
| Running in Codex, Gemini CLI, or any non-Claude agent | `thesis-openalex-expand` |
| Automated snowballing pipeline | `thesis-openalex-expand` |

## Workflow

1. Start from one or more seed papers already marked `keep` or `maybe`. Resolve their OpenAlex IDs from DOI.
2. Choose expansion direction per paper:
   - **Backward** (what this paper cites): `GET /works/SEED_ID/references`
   - **Forward** (what cites this paper): `GET /works?filter=cites:SEED_ID&sort=cited_by_count:desc`
   - **Co-citation** (what appears alongside this paper in reference lists): use concepts filter
3. Deduplicate across seed papers using DOI as key.
4. Filter by `publication_year`, `type:article`, concept relevance.
5. Label each result: direct continuation, adjacent method, background source, or out-of-scope.
6. Extract recurring authors and concept clusters.
7. Before finalizing output, read `references/quality-check.md`.

## Execution Modes

### Mode 1 — Resolve OpenAlex ID from DOI

```
GET https://api.openalex.org/works/https://doi.org/DOI
```

Returns the work object with `id` field like `https://openalex.org/W2741809807`.

### Mode 2 — Forward citations (papers that cite the seed)

```
GET https://api.openalex.org/works?filter=cites:OPENALEX_ID&sort=cited_by_count:desc&per-page=20&select=id,doi,title,authorships,publication_year,cited_by_count,concepts&mailto=YOUR_EMAIL
```

### Mode 3 — Backward citations (what the seed paper cites)

```
GET https://api.openalex.org/works/OPENALEX_ID/references?select=id,doi,title,authorships,publication_year,cited_by_count&per-page=20&mailto=YOUR_EMAIL
```

### Mode 4 — Related works by concept

```
GET https://api.openalex.org/works?filter=concepts.id:CONCEPT_ID,publication_year:>2015&sort=cited_by_count:desc&per-page=20&mailto=YOUR_EMAIL
```

Get concept IDs from the seed paper's `concepts` field.

### Mode 5 — Python script (Codex / Gemini / any bash-capable agent)

```bash
python scripts/api/openalex_expand.py "10.1016/j.ijheh.2020.113629" --direction both
```

## Relationship Labels

| Signal | Label |
| --- | --- |
| Same concept cluster, same methods | `direct_continuation` |
| Overlapping concepts, different methods | `adjacent_method` |
| Cited by seed but lower concept overlap | `background` |
| Low concept overlap, different population | `out_of_scope` |

## Output Contract

Return matching `schemas/openalex-expand.schema.json`:

```json
{
  "platform": "OpenAlex",
  "seed_papers": [
    { "title": "seed title", "doi": "10.xxxx/xxxx", "openalex_id": "W..." }
  ],
  "related_papers": [
    {
      "title": "paper title",
      "authors": [],
      "year": null,
      "doi": null,
      "url": null,
      "cited_by_count": 0,
      "relationship": "direct_continuation",
      "decision": "maybe",
      "notes": "why it is related"
    }
  ],
  "authors_to_watch": [],
  "concept_clusters": [],
  "next_searches": []
}
```

`relationship` must be one of: `direct_continuation`, `adjacent_method`, `background`, `out_of_scope`.

## Generic Mode

If no HTTP access, produce a literature expansion plan:
- seed criteria
- concept IDs to search
- author tracking instructions
- follow-up API queries to run

Label it as a search plan, not live OpenAlex results.
