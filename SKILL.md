---
name: pubmed-search
description: >-
  Search PubMed for biomedical papers by topic, author, or DOI with query approval and hit-count preview;
  retrieve metadata and abstracts by PMID. Use for PubMed or biomedical reference retrieval,
  not private-library searches, manuscript citation evaluation, or merely discussing PubMed.
---

# PubMed Search

Search PubMed via the official NCBI E-utilities API. No API key required for basic use (≤3 req/sec).

Use `literature-scout` when the task requires evaluating references against manuscript claims or comparing sources, and `readcube-papers` for the user's saved library. PMC full text, citation matching, and cross-database links belong to `pubmed-database` when available; do not switch skills merely to bypass this workflow's approval gates.

## Workflow

For discovery searches, obtain query approval, show the hit `count`, then obtain explicit approval of the selected query and retrieval size before running `search` or fetching candidate abstracts. Do not retrieve paper lists preemptively. A direct request for an already supplied PMID may use `fetch` without a discovery search.

When a user requests a PubMed search, follow this workflow:

### Step 1: Understand the Research Topic

Clarify the user's search intent:

- What is the biological topic or question?
- Are they looking for a specific paper, a focused set, or a broad survey?
- Any filters? (year range, organism, article type, specific authors)

### Step 2: Propose Search Queries for Approval

When designing or adjusting queries, read [search-design.md](references/search-design.md) for synonym expansion, scope targets, and field tags. Present 1–3 queries at different specificity levels with brief explanations and obtain approval before running them. Confirm whether to include reviews if not already specified. If the user requests modifications, update the queries and re-present.

### Step 3: Show Hit Counts

After query approval, write each query to a temporary file and run `count` using the CLI below. File creation and counting need no additional approval. Show the query labels and hit counts only; do not run `search` yet.

### Step 4: User Reviews Hit Counts

Wait for the user to review the hit counts and decide:

- **Approve**: Proceed to execute the selected query
- **Adjust**: Modify query terms and re-count
- **Change scope**: Try a narrower or broader strategy

### Step 5: Execute Search

After the user approves the displayed count, selected query, and retrieval size, run the search without asking again:

```bash
python scripts/pubmed_search.py --format markdown search --query-file "<query-file>" --max <N>
```

Recommended `--max` values: Narrow=20, Moderate=50, Broad=200.

### Step 6: Present Results

Show results in a readable format. For key papers, fetch full details:

```bash
python scripts/pubmed_search.py --format markdown fetch <PMID>
```

### Step 7: Ask to Save Results

After presenting the search results, ask whether to save them as `.csv` or `.md` if the user has not already specified this.

If the user agrees, run the following command to save the results directly. You may auto-run this without further asking.

```bash
python scripts/pubmed_search.py --format csv --output results.csv search --query-file "<query-file>" --max <N>
```

### Step 8: Ask to Delete Intermediate Files

After the search workflow is complete and any requested result saving is handled, **always ask the user** whether to delete intermediate files created during the workflow, such as temporary query files or scratch output files.

Only delete these intermediate files after the user explicitly agrees. Do not delete saved search results unless the user specifically asks for that.

When deleting files, state which files will be removed before running the deletion command.

## CLI Commands

Resolve `scripts/` from this skill directory. `python` below means the host's configured interpreter, not necessarily a command on PATH. `count` and `search` accept `--query-file`; `fetch` accepts a PMID instead. Global `--format` and `--output` options precede the subcommand.

Write the query as a single UTF-8 line without BOM; the script reads only the first line. On Windows PowerShell, always use `--query-file`: quotes and spaces in direct query arguments can be mangled, and default file redirection may use the wrong encoding. Use the host's UTF-8 file-writing method and a valid temporary path, not an assumed `/tmp` directory.

```bash
# Count hits
python scripts/pubmed_search.py count --query-file "<query-file>"

# Search with results (Markdown format)
python scripts/pubmed_search.py --format markdown search --query-file "<query-file>" --max 20

# Search and save to file (CSV or Markdown) to avoid encoding issues in terminal
python scripts/pubmed_search.py --format csv --output results.csv search --query-file "<query-file>" --max 20
python scripts/pubmed_search.py --format markdown --output results.md search --query-file "<query-file>" --max 20

# Fetch details for a specific paper
python scripts/pubmed_search.py --format markdown fetch 32553272

# Sort options: relevance (default), pub_date, first_author
python scripts/pubmed_search.py search --query-file "<query-file>" --max 30 --sort pub_date
```

`--output` writes UTF-8 without BOM. If the host requires Excel-compatible CSV (`utf-8-sig`), add the BOM to the saved CSV before delivery; do not apply it to query files.

## Optional: API Key

For heavy use (>3 req/sec), the script accepts an existing `NCBI_API_KEY` environment variable. Have the user configure a key privately if needed; do not print it or write it into the skill.

Get one at https://www.ncbi.nlm.nih.gov/account/settings/
