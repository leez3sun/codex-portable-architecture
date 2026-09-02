# Quality Check — OpenAlex Search

Base rules: see `docs/quality-standards.md`.

## OpenAlex-Specific

- Reconstruct abstracts from `abstract_inverted_index` before presenting results. Do not report papers without reconstructed abstracts as if you read them directly.
- `cited_by_count` is total citations — not split into supporting/contrasting. Do not report it as evidence quality.
- OpenAlex concepts are machine-assigned. Use them for relevance filtering, not as ground truth for topic classification.
- Include the `api_url` in output so the search is reproducible.
- If zero results, broaden query terms or remove filters before reporting no evidence.
- Open access papers with `open_access_url` should be flagged — they can be read fully, not just by abstract.
