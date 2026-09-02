# Quality Check — OpenAlex Expand

Base rules: see `docs/quality-standards.md`.

## OpenAlex-Specific

- Seed papers must already be `keep` or `maybe`. Do not expand from `reject`.
- Deduplicate by DOI across all seed papers before returning related work. The same paper appearing under two seeds is one result, not two.
- `relationship` labels must be justified by concept overlap or citation path — not guessed from title alone.
- Forward citations sorted by `cited_by_count` bias toward older papers. Use `publication_date:desc` to surface recent work separately.
- Do not expand more than 3 seeds in a single call — result sets compound quickly. Report `total_results` so the user knows what was trimmed.
