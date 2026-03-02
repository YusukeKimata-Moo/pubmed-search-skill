# PubMed Search Skill

An **agent skill** for AI coding assistants (e.g., [Antigravity](https://antigravity.google/), [Claude Code](https://claude.com/product/claude-code)) that searches [PubMed](https://pubmed.ncbi.nlm.nih.gov/) for biomedical and molecular biology literature using the official NCBI E-utilities API.

This skill enables AI agents to propose optimized search strategies, execute PubMed queries, and retrieve paper metadata and abstracts — useful for literature reviews, manuscript preparation, and reference management.

## Features

- 🔍 **Smart search strategy** — Agent proposes three query patterns (Narrow / Moderate / Broad) and lets you choose
- 📊 **Hit count preview** — Check expected results before executing a full search
- 📝 **Rich metadata** — Title, authors, journal, DOI, abstract, MeSH terms, keywords
- 📄 **Multiple output formats** — JSON or Markdown
- 🔓 **No API key required** — Uses the public NCBI E-utilities API (optional API key for heavy use)
- 📦 **Zero dependencies** — Uses only Python standard library

## What is an Agent Skill?

Agent skills are modular packages that extend the capabilities of AI coding agents. When installed in the `~/.agents/skills/` directory, the agent automatically detects and uses the skill based on user requests.

### Installation

```bash
git clone https://github.com/YusukeKimata-Moo/pubmed-search-skill.git ~/.agents/skills/pubmed-search
```

## Usage

### Example Prompts

**Basic searches:**

- _"Search PubMed for recent papers about CRISPR-Cas9 genome editing"_
- _"Find review articles on autophagy in cancer"_
- _"Look up papers by Yamanaka on iPSC reprogramming"_

**Targeted searches:**

- _"Find papers about mRNA vaccine delivery published in Nature in 2024"_
- _"Search PubMed for studies on BRCA1 and homologous recombination"_
- _"Look for recent papers on single-cell RNA-seq methods"_

**Detailed retrieval:**

- _"Get the abstract and details for PMID 32553272"_
- _"Find the DOI and MeSH terms for that paper"_

**Manuscript support:**

- _"Find references about protein ubiquitination for my Introduction"_
- _"Search for key papers on mitochondrial dynamics to cite in my Discussion"_

### How It Works

1. You describe your research topic
2. The agent proposes **search queries with explanations** and asks whether to include/exclude reviews
3. You approve or adjust the queries
4. The agent shows **hit counts only** — you decide if the scope is right
5. You select a query to execute
6. The agent runs the search and presents results

### CLI Reference

The agent calls the script internally, but you can also use it directly:

```bash
# Write query to file (recommended for complex queries with quotes)
echo '"CRISPR"[TI] AND "review"[PT]' > /tmp/q.txt

python scripts/pubmed_search.py count --query-file /tmp/q.txt                  # Count hits
python scripts/pubmed_search.py search --query-file /tmp/q.txt --max 20        # Search (JSON)
python scripts/pubmed_search.py --format markdown search --query-file /tmp/q.txt --max 50  # Markdown
python scripts/pubmed_search.py --format markdown fetch 32553272               # Fetch details
python scripts/pubmed_search.py count "simple query"                           # Direct query (simple)
```

## Requirements

- Python 3.7+
- No external dependencies

## Optional: NCBI API Key

For heavy use (>3 requests/second), register for an API key:

1. Create an account at [NCBI](https://www.ncbi.nlm.nih.gov/account/)
2. Go to [Settings](https://www.ncbi.nlm.nih.gov/account/settings/)
3. Generate an API key
4. Set environment variable:

```bash
export NCBI_API_KEY="your_api_key"
```

## API Endpoints Used

| Endpoint                                              | Purpose                    |
| ----------------------------------------------------- | -------------------------- |
| `eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`  | Search queries, hit counts |
| `eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi` | Paper summaries            |
| `eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`   | Full details + abstracts   |

## Acknowledgments

This skill uses the [NCBI E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25497/), a public API provided by the National Center for Biotechnology Information.

## License

MIT
