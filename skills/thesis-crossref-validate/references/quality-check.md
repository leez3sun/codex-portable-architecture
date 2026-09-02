# Quality Check — CrossRef Validate

Base rules: see `docs/quality-standards.md`.

## CrossRef-Specific

- CrossRef `is-referenced-by-count` is citation count — NOT the same as Scite Smart Citations. Never label it "supporting citations".
- Check `update-to` field for retraction or correction records. Any retraction = `risk_level: high`, `decision: reject`.
- If DOI lookup fails (404), try the title query endpoint before reporting the paper as unverifiable.
- Supplement with Semantic Scholar when `influentialCitationCount` matters for risk assessment.
- CrossRef metadata can be incomplete for older papers. Missing `abstract` or `license` is not itself a risk signal.
