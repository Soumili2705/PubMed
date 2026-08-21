from __future__ import annotations
import xml.etree.ElementTree as ET
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


@st.cache_data(ttl=3600, show_spinner=False)
def search_pubmed(query: str, max_results: int = 15) -> list[str]:
  """Searches NCBI ESearch using the MeSH-expanded Boolean query."""
  params = {
      "db": "pubmed",
      "term": query,
      "retmode": "json",
      "retmax": max_results,
      "sort": "relevance",
  }
  if email := os.getenv("NCBI_EMAIL"):
    params["email"] = email
  try:
    response = requests.get(PUBMED_SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])
  except Exception as e:
    print(f"ESearch API Error: {e}")
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_papers_cached(pmids: tuple[str, ...]) -> list[dict]:
  """Fetches XML records from NCBI EFetch and parses titles, abstracts, journals, and publication year."""
  if not pmids:
    return []

  params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
  if email := os.getenv("NCBI_EMAIL"):
    params["email"] = email

  try:
    response = requests.get(PUBMED_FETCH_URL, params=params, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    papers = []

    for article in root.findall(".//PubmedArticle"):
      pmid_element = article.find(".//PMID")
      title_element = article.find(".//ArticleTitle")
      abstract_elements = article.findall(".//AbstractText")
      journal_element = article.find(".//Journal/Title")

      # Publication Year extraction
      year_element = article.find(".//Journal/JournalIssue/PubDate/Year")
      if year_element is None:
        year_element = article.find(".//ArticleDate/Year")
      if year_element is None:
        year_element = article.find(".//DateCompleted/Year")

      # Author extraction
      first_author = ""
      author_elem = article.find(".//AuthorList/Author[1]/LastName")
      if author_elem is not None and author_elem.text:
        first_author = f"{author_elem.text} et al."

      pmid = pmid_element.text if pmid_element is not None else ""
      title = (
          "".join(title_element.itertext())
          if title_element is not None
          else "No Title"
      )
      abstract = " ".join(
          "".join(elem.itertext()) for elem in abstract_elements
      )
      journal = (
          journal_element.text if journal_element is not None else "PubMed"
      )
      year = (
          year_element.text
          if year_element is not None and year_element.text
          else "Recent"
      )

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
  """Fetches PubMed records, caching repeated result sets for one hour."""
  return _fetch_papers_cached(tuple(pmids))
