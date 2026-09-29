# PubMed Query Design

Read when designing or adjusting a discovery query; not needed for direct PMID retrieval.

Avoid overly restrictive queries. Expand concise user keywords with `OR` for related concepts, synonyms, and biological processes; for example, consider "polarity" alongside "asymmetric division". Explain expansions when presenting queries for approval.

- **Narrow (target: ≤10 hits):** specific MeSH `[MH]` or title `[TI]` terms, multiple AND, organism/method filters.
- **Moderate (target: 20–50 hits):** MeSH plus free-text `[TIAB]`, date/type filters, synonyms joined with OR.
- **Broad (target: 100–200 hits):** general terms, fewer AND, no date restriction, related pathways/anatomical structures/concepts.

These are query-design targets, not permission to retrieve results. Suggested retrieval caps remain Narrow=20, Moderate=50, Broad=200, subject to the user's approved size.

Confirm inclusion or exclusion of reviews if not already specified. To exclude them, add `NOT "Review"[PT]`.

| Tag | Field | Example |
| --- | --- | --- |
| `[TI]` | Title only | `"apoptosis"[TI]` |
| `[TIAB]` | Title + Abstract | `"Western blot"[TIAB]` |
| `[AU]` | Author | `"Yamanaka S"[AU]` |
| `[MH]` | MeSH heading | `"Signal Transduction"[MH]` |
| `[PT]` | Publication type | `"Review"[PT]` |
| `[DP]` | Date of publication | `"2020/01:2024/12"[DP]` |
| `[LA]` | Language | `"English"[LA]` |
| `[JT]` | Journal title | `"Nature"[JT]` |
