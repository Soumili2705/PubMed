from __future__ import annotations
import os
import xml.etree.ElementTree as ET
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DEFAULT_TIMEOUT = 30


def _get_xml_text(elem: ET.Element, paths: list[str], default: str = "") -> str:
    """Extracts text from the first matching XPath selector."""
    for path in paths:
        if (target := elem.find(path)) is not None and target.text:
            return target.text.strip()
    return default


@st.cache_data(ttl=3600, show_spinner=False)
def search_pubmed(query: str, max_results: int = 15) -> list[str]:
    """Searches NCBI ESearch using the MeSH-expanded Boolean query."""
    term = f"({query}) AND hasabstract[text]" if "hasabstract" not in query.lower() else query
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": max(max_results * 2, 20),
        "sort": "relevance",
    }
    if email := os.getenv("NCBI_EMAIL"):
        params["email"] = email

    try:
        response = requests.get(PUBMED_SEARCH_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"ESearch API Error: {e}")
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_papers_cached(pmids: tuple[str, ...]) -> list[dict]:
    """Fetches XML records from NCBI EFetch and parses metadata."""
    if not pmids:
        return []

    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    if email := os.getenv("NCBI_EMAIL"):
        params["email"] = email

    try:
        response = requests.get(PUBMED_FETCH_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        papers: list[dict] = []

        for article in root.findall(".//PubmedArticle"):
            pmid = _get_xml_text(article, [".//PMID"])
            title_elem = article.find(".//ArticleTitle")
            title = "".join(title_elem.itertext()) if title_elem is not None else "No Title"
            abstract_elems = article.findall(".//AbstractText")
            abstract = " ".join("".join(elem.itertext()) for elem in abstract_elems)
            journal = _get_xml_text(article, [".//Journal/Title"], default="PubMed")
            year = _get_xml_text(
                article,
                [".//Journal/JournalIssue/PubDate/Year", ".//ArticleDate/Year", ".//DateCompleted/Year"],
                default="Recent"
            )
            author_last = _get_xml_text(article, [".//AuthorList/Author[1]/LastName"])
            first_author = f"{author_last} et al." if author_last else ""

            if abstract.strip():
                papers.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "author": first_author,
                })
        return papers
    except Exception as e:
        print(f"EFetch API Error: {e}")
        return []


def fetch_papers(pmids: list[str]) -> list[dict]:
    """Public wrapper to fetch PubMed records with tuple-caching."""
    return _fetch_papers_cached(tuple(pmids))
