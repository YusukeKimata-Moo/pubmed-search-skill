---
name: pubmed-search
description: >-
  Search PubMed for molecular biology and biomedical research papers using NCBI E-utilities API.
  Use when the user requests: searching PubMed for papers, finding references on a specific topic,
  building a bibliography, looking up papers by author/keyword/DOI, or retrieving paper abstracts
  and metadata from PubMed. Triggers on mentions of "PubMed", "literature search", "find papers",
  "search for references", or requests to look up biomedical literature.
---

# PubMed Search

Search PubMed via the official NCBI E-utilities API. No API key required for basic use (≤3 req/sec).

## Workflow

> **CRITICAL MANDATORY RULE**: You MUST NEVER execute a full `search` without first showing the user the hit `count` and getting their explicit approval for the number of results. Do not preemptively retrieve abstracts or paper lists. ALWAYS present hit counts first.

When a user requests a PubMed search, follow this workflow:

### Step 1: Understand the Research Topic

Clarify the user's search intent:

- What is the biological topic or question?
- Are they looking for a specific paper, a focused set, or a broad survey?
- Any filters? (year range, organism, article type, specific authors)

### Step 2: Propose Search Queries for Approval

Design 1–3 PubMed search queries at different specificity levels. **Before running any queries, present them to the user with explanations** for approval. Also ask whether to include or exclude review articles.

Present in this format:

---

**Your topic**: [user's topic]

**Proposed queries**:

| #     | Query              | Explanation                       |
| ----- | ------------------ | --------------------------------- |
| **A** | `[specific query]` | [why this query, what it targets] |
| **B** | `[balanced query]` | [why this query, what it targets] |
| **C** | `[wide query]`     | [why this query, what it targets] |

**Review articles**: Include or exclude? (adding `NOT "Review"[PT]` to exclude)

Shall I proceed with these queries? (or suggest modifications)

---

Wait for user approval before proceeding. If the user requests modifications, update the queries and re-present.

### Step 3: Show Hit Counts

After user approves the queries, write each to a temporary file and run `count`. **Show only the hit counts — do NOT execute the full search yet.**

_You may auto-run the file creation and `count` commands without asking the user for permission._

```bash
// turbo
# Write query to a temp file to avoid shell quoting issues
echo '<query>' > /tmp/pubmed_q.txt
python scripts/pubmed_search.py --format markdown count --query-file /tmp/pubmed_q.txt
```

Present results:

---

| Strategy | Hits |
| -------- | ---- |
| **A**    | N    |
| **B**    | N    |
| **C**    | N    |

Which query to execute? (A/B/C, or I can adjust)

---

### Search Query Design Guidelines

> **CRITICAL: Avoid overly restrictive queries.** Users often provide a concise keyword, but you should expand the search using `OR` to include related biological concepts, synonyms, and associated processes (e.g., if the user asks for "asymmetric division", include "polarity").

**Narrow (target: ≤10 hits)**: Specific MeSH [MH] or title [TI] terms, multiple AND, organism/method filters.

**Moderate (target: 20-50 hits)**: MeSH + free-text [TIAB], date/type filters. Use `OR` to include related keywords and synonyms to ensure relevant papers aren't missed.

**Broad (target: 100-200 hits)**: General terms, fewer AND, no date restriction. Actively expand the scope to related pathways, anatomical structures, or broader concepts.

### Useful PubMed Search Fields

| Tag      | Field               | Example                     |
| -------- | ------------------- | --------------------------- |
| `[TI]`   | Title only          | `"apoptosis"[TI]`           |
| `[TIAB]` | Title + Abstract    | `"Western blot"[TIAB]`      |
| `[AU]`   | Author              | `"Yamanaka S"[AU]`          |
| `[MH]`   | MeSH heading        | `"Signal Transduction"[MH]` |
| `[PT]`   | Publication type    | `"Review"[PT]`              |
| `[DP]`   | Date of publication | `"2020/01:2024/12"[DP]`     |
| `[LA]`   | Language            | `"English"[LA]`             |
| `[JT]`   | Journal title       | `"Nature"[JT]`              |

### Step 4: User Reviews Hit Counts

Wait for the user to review the hit counts and decide:

- **Approve**: Proceed to execute the selected query
- **Adjust**: Modify query terms and re-count
- **Change scope**: Try a narrower or broader strategy

### Step 5: Execute Search

After user approves a query:

_You may auto-run the search command below without asking._

```bash
// turbo
python scripts/pubmed_search.py --format markdown search --query-file /tmp/pubmed_q.txt --max <N>
```

Recommended `--max` values: Narrow=20, Moderate=50, Broad=200.

### Step 6: Present Results

Show results in a readable format. For key papers, fetch full details:

_You may auto-run the fetch command below without asking._

```bash
// turbo
python scripts/pubmed_search.py --format markdown fetch <PMID>
```

### Step 7: Ask to Save Results

After presenting the search results, **always ask the user** if they would like to save the retrieved results to a file (e.g., as `.csv` or `.md`).

If the user agrees, run the following command to save the results directly. You may auto-run this without further asking.

```bash
// turbo
python scripts/pubmed_search.py --format csv --output results.csv search --query-file /tmp/pubmed_q.txt --max <N>
```

## CLI Commands

All commands support `--query-file` to read the query from a file (recommended for complex queries with quotes/spaces):

```bash
# Write query to file (avoids shell quoting issues)
echo '"CRISPR"[TI] AND "review"[PT]' > /tmp/q.txt

# Count hits
python scripts/pubmed_search.py count --query-file /tmp/q.txt

# Search with results (Markdown format)
python scripts/pubmed_search.py --format markdown search --query-file /tmp/q.txt --max 20

# Search and save to file (CSV or Markdown) to avoid encoding issues in terminal
python scripts/pubmed_search.py --format csv --output results.csv search --query-file /tmp/q.txt --max 20
python scripts/pubmed_search.py --format markdown --output results.md search --query-file /tmp/q.txt --max 20

# Fetch details for a specific paper
python scripts/pubmed_search.py --format markdown fetch 32553272

# Sort options: relevance (default), pub_date, first_author
python scripts/pubmed_search.py search --query-file /tmp/q.txt --max 30 --sort pub_date

# Direct query (simple queries without special chars)
python scripts/pubmed_search.py count "simple query"
```

> **Note (Windows)**: On PowerShell, PubMed queries containing double quotes and spaces are mangled by the shell. Always use `--query-file` instead of passing queries directly on the command line.

## Optional: API Key

For heavy use (>3 req/sec), set an NCBI API key:

```bash
export NCBI_API_KEY="your_api_key"
```

Get one at https://www.ncbi.nlm.nih.gov/account/settings/
