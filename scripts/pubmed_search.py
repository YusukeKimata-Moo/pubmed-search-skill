#!/usr/bin/env python3
"""
PubMed search client using NCBI E-utilities API.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET

# Fix encoding for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL_NAME = "pubmed_search_skill"
CONTACT_EMAIL = "pubmed_search_skill@example.com"


def _build_params(params: dict) -> str:
    """Build URL query parameters with tool/email."""
    params["tool"] = TOOL_NAME
    email = os.environ.get("NCBI_EMAIL", CONTACT_EMAIL)
    params["email"] = email
    api_key = os.environ.get("NCBI_API_KEY", "")
    if api_key:
        params["api_key"] = api_key
    return urllib.parse.urlencode(params)


def _get_xml(url: str) -> ET.Element:
    """Fetch URL and parse XML response."""
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    return ET.fromstring(data)


def esearch_count(query: str) -> int:
    """Get hit count for a query without retrieving results."""
    params = _build_params({
        "db": "pubmed",
        "term": query,
        "rettype": "count",
    })
    url = f"{EUTILS_BASE}/esearch.fcgi?{params}"
    root = _get_xml(url)
    count_el = root.find("Count")
    return int(count_el.text) if count_el is not None else 0


def esearch(query: str, retmax: int = 20, sort: str = "relevance") -> dict:
    """Search PubMed and return PMIDs + count."""
    params = _build_params({
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "sort": sort,
        "retmode": "json",
    })
    url = f"{EUTILS_BASE}/esearch.fcgi?{params}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    result = data.get("esearchresult", {})
    return {
        "count": int(result.get("count", 0)),
        "ids": result.get("idlist", []),
        "query_translation": result.get("querytranslation", ""),
    }


def esummary(pmids: list) -> list:
    """Get document summaries for a list of PMIDs."""
    if not pmids:
        return []
    params = _build_params({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
    })
    url = f"{EUTILS_BASE}/esummary.fcgi?{params}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    result = data.get("result", {})
    items = []
    for pmid in pmids:
        if pmid in result:
            r = result[pmid]
            authors = [a.get("name", "") for a in r.get("authors", [])]
            items.append({
                "pmid": pmid,
                "title": r.get("title", ""),
                "authors": authors,
                "journal": r.get("fulljournalname", r.get("source", "")),
                "journal_abbrev": r.get("source", ""),
                "year": r.get("pubdate", "")[:4],
                "pubdate": r.get("pubdate", ""),
                "volume": r.get("volume", ""),
                "issue": r.get("issue", ""),
                "pages": r.get("pages", ""),
                "doi": _extract_doi(r.get("elocationid", "")),
                "pubtype": r.get("pubtype", []),
            })
    return items


def efetch_abstract(pmid: str) -> dict:
    """Fetch detailed info including abstract for a single PMID."""
    params = _build_params({
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
    })
    url = f"{EUTILS_BASE}/efetch.fcgi?{params}"
    root = _get_xml(url)

    article = root.find(".//PubmedArticle")
    if article is None:
        return None

    # Title
    title_el = article.find(".//ArticleTitle")
    title = _get_text_content(title_el) if title_el is not None else ""

    # Abstract
    abstract_parts = []
    for abs_text in article.findall(".//Abstract/AbstractText"):
        label = abs_text.get("Label", "")
        text = _get_text_content(abs_text)
        if label:
            abstract_parts.append(f"{label}: {text}")
        else:
            abstract_parts.append(text)
    abstract = "\n".join(abstract_parts)

    # Authors
    authors = []
    for author in article.findall(".//Author"):
        last = author.findtext("LastName", "")
        first = author.findtext("ForeName", "")
        if last:
            authors.append(f"{last} {first}".strip())

    # Journal
    journal = article.findtext(".//Journal/Title", "")
    journal_abbrev = article.findtext(".//Journal/ISOAbbreviation", "")
    year = article.findtext(".//PubDate/Year", "")
    if not year:
        medline_date = article.findtext(".//PubDate/MedlineDate", "")
        if medline_date:
            year = medline_date[:4]
    volume = article.findtext(".//Volume", "")
    issue = article.findtext(".//Issue", "")
    pages = article.findtext(".//MedlinePgn", "")

    # DOI
    doi = ""
    for aid in article.findall(".//ArticleId"):
        if aid.get("IdType") == "doi":
            doi = aid.text or ""
            break
    if not doi:
        eloc = article.find(".//ELocationID[@EIdType='doi']")
        if eloc is not None:
            doi = eloc.text or ""

    # MeSH terms
    mesh_terms = []
    for mesh in article.findall(".//MeshHeading/DescriptorName"):
        mesh_terms.append(mesh.text or "")

    # Keywords
    keywords = []
    for kw in article.findall(".//Keyword"):
        keywords.append(kw.text or "")

    return {
        "pmid": pmid,
        "title": title,
        "authors": authors,
        "journal": journal,
        "journal_abbrev": journal_abbrev,
        "year": year,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "doi": doi,
        "abstract": abstract,
        "mesh_terms": mesh_terms,
        "keywords": keywords,
    }


def _get_text_content(element) -> str:
    """Get all text content from an XML element, including tail text of children."""
    if element is None:
        return ""
    parts = []
    parts.append(element.text or "")
    for child in element:
        parts.append(_get_text_content(child))
        parts.append(child.tail or "")
    return "".join(parts).strip()


def _extract_doi(elocationid: str) -> str:
    """Extract DOI from elocationid string like 'doi: 10.xxxx/yyyy'."""
    if "doi:" in elocationid.lower():
        return elocationid.split(":", 1)[1].strip()
    if elocationid.startswith("10."):
        return elocationid
    return ""


def format_markdown_summary(items: list) -> str:
    """Format search results as markdown."""
    lines = []
    for i, item in enumerate(items, 1):
        authors_str = ", ".join(item.get("authors", [])[:3])
        if len(item.get("authors", [])) > 3:
            authors_str += " et al."
        title = item.get("title", "No title")
        year = item.get("year", "N/A")
        journal = item.get("journal", "")
        doi = item.get("doi", "")
        pmid = item.get("pmid", "")

        lines.append(f"### {i}. {title}")
        lines.append(f"- **Authors**: {authors_str}")
        lines.append(f"- **Journal**: {journal} ({year})")
        if doi:
            lines.append(f"- **DOI**: [{doi}](https://doi.org/{doi})")
        lines.append(f"- **PMID**: [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
        lines.append("")
    return "\n".join(lines)


def format_markdown_detail(item: dict) -> str:
    """Format detailed paper info as markdown."""
    lines = []
    title = item.get("title", "No title")
    authors_str = ", ".join(item.get("authors", []))
    year = item.get("year", "N/A")
    journal = item.get("journal", "")
    doi = item.get("doi", "")
    pmid = item.get("pmid", "")

    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Authors**: {authors_str}")
    lines.append(f"**Journal**: {journal} ({year})")
    vol = item.get("volume", "")
    issue = item.get("issue", "")
    pages = item.get("pages", "")
    if vol:
        ref = f"{vol}"
        if issue:
            ref += f"({issue})"
        if pages:
            ref += f":{pages}"
        lines.append(f"**Reference**: {ref}")
    if doi:
        lines.append(f"**DOI**: [{doi}](https://doi.org/{doi})")
    lines.append(f"**PMID**: [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
    lines.append("")

    abstract = item.get("abstract", "")
    if abstract:
        lines.append("## Abstract")
        lines.append("")
        lines.append(abstract)
        lines.append("")

    mesh = item.get("mesh_terms", [])
    if mesh:
        lines.append(f"**MeSH Terms**: {', '.join(mesh)}")

    keywords = item.get("keywords", [])
    if keywords:
        lines.append(f"**Keywords**: {', '.join(keywords)}")

    return "\n".join(lines)


def _resolve_query(args) -> str:
    """Resolve query from positional arg or --query-file."""
    query_file = getattr(args, "query_file", None)
    query = getattr(args, "query", None)
    if query_file:
        with open(query_file, "r", encoding="utf-8") as f:
            return f.readline().strip()
    if query:
        return query
    print("Error: either query or --query-file is required.", file=sys.stderr)
    sys.exit(1)


def _add_query_args(parser):
    """Add query and --query-file arguments to a subparser."""
    parser.add_argument("query", nargs="?", default=None, help="PubMed search query")
    parser.add_argument(
        "--query-file", dest="query_file", default=None,
        help="Read query from file (1st line). Use this to avoid shell quoting issues.",
    )


def main():
    parser = argparse.ArgumentParser(
        description="PubMed search via NCBI E-utilities API",
    )
    parser.add_argument(
        "--format", choices=["json", "markdown"], default="json",
        help="Output format (default: json)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # count
    count_parser = subparsers.add_parser("count", help="Get hit count for a query")
    _add_query_args(count_parser)

    # search
    search_parser = subparsers.add_parser("search", help="Search PubMed")
    _add_query_args(search_parser)
    search_parser.add_argument(
        "--max", type=int, default=20, dest="retmax",
        help="Maximum results to return (default: 20)",
    )
    search_parser.add_argument(
        "--sort", choices=["relevance", "pub_date", "first_author"],
        default="relevance", help="Sort order (default: relevance)",
    )

    # fetch
    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch detailed info for a PMID",
    )
    fetch_parser.add_argument("pmid", help="PubMed ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    output_format = args.format

    if args.command == "count":
        query = _resolve_query(args)
        count = esearch_count(query)
        if output_format == "json":
            print(json.dumps({"query": query, "count": count}, indent=2))
        else:
            print(f"**Query**: `{query}`")
            print(f"**Hit count**: {count:,}")

    elif args.command == "search":
        query = _resolve_query(args)
        print(f"Searching: {query}", file=sys.stderr)
        search_result = esearch(query, retmax=args.retmax, sort=args.sort)
        count = search_result["count"]
        pmids = search_result["ids"]
        query_translation = search_result["query_translation"]
        print(
            f"Found {count:,} results, retrieving top {len(pmids)}...",
            file=sys.stderr,
        )

        items = []
        if pmids:
            # Batch in groups of 200 for ESummary
            for i in range(0, len(pmids), 200):
                batch = pmids[i : i + 200]
                items.extend(esummary(batch))
                if i + 200 < len(pmids):
                    time.sleep(0.34)  # Rate limit: 3 req/sec

        if output_format == "json":
            print(json.dumps({
                "query": query,
                "query_translation": query_translation,
                "total_count": count,
                "returned": len(items),
                "items": items,
            }, indent=2, ensure_ascii=False))
        else:
            print(f"# PubMed Search Results\n")
            print(f"**Query**: `{query}`")
            if query_translation:
                print(f"**Translated query**: `{query_translation}`")
            print(f"**Total hits**: {count:,} | **Showing**: {len(items)}\n")
            print(format_markdown_summary(items))

    elif args.command == "fetch":
        item = efetch_abstract(args.pmid)
        if item:
            if output_format == "json":
                print(json.dumps(item, indent=2, ensure_ascii=False))
            else:
                print(format_markdown_detail(item))
        else:
            print(f"PMID {args.pmid} not found.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
