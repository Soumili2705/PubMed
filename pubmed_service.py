import os
from Bio import Entrez
import chromadb
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Required by NCBI PubMed API
Entrez.email = "soumilibanerjee312@gmail.com"

# Initialize local ChromaDB
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="safe_pubmed_mvp")

# Initialize Groq Client for AI chat
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def fetch_and_store_pubmed_articles(query_term, max_results=6):
  """Fetches real papers from PubMed API and stores them in ChromaDB."""
  try:
    # 1. Search PubMed for IDs using user query directly (Safe & Predictable)
    search_handle = Entrez.esearch(
        db="pubmed", term=query_term, retmax=max_results
    )
    search_results = Entrez.read(search_handle)
    search_handle.close()

    id_list = search_results.get("IdList", [])
    if not id_list:
      return False

    # 2. Fetch paper XML details
    fetch_handle = Entrez.efetch(
        db="pubmed", id=id_list, rettype="abstract", retmode="xml"
    )
    articles_data = Entrez.read(fetch_handle)
    fetch_handle.close()

    documents = []
    metadatas = []
    ids = []

    # 3. Parse articles safely
    for paper in articles_data.get("PubmedArticle", []):
      try:
        medline_cit = paper.get("MedlineCitation", {})
        pmid = str(medline_cit.get("PMID", ""))
        article_info = medline_cit.get("Article", {})
        title = article_info.get("ArticleTitle", "No Title")

        abstract_elem = article_info.get("Abstract", {}).get("AbstractText", [])
        if not abstract_elem:
          continue
        abstract_text = " ".join([str(e) for e in abstract_elem])

        documents.append(abstract_text)
        metadatas.append({"title": title, "pmid": pmid})
        ids.append(pmid)
      except Exception:
        continue

    if documents:
      # Clear old data and add fresh vectors
      existing = collection.get()
      if existing["ids"]:
        collection.delete(ids=existing["ids"])
      collection.add(documents=documents, metadatas=metadatas, ids=ids)

    return True
  except Exception as e:
    print(f"PubMed Fetch Error: {e}")
    return False


def semantic_search_pubmed(user_query, n_results=5):
  """Finds the most relevant stored papers using vector similarity."""
  try:
    results = collection.query(query_texts=[user_query], n_results=n_results)
    formatted = []

    if results and "metadatas" in results and results["metadatas"]:
      for meta, doc, dist in zip(
          results["metadatas"][0],
          results["documents"][0],
          results["distances"][0],
      ):
        # Calculate a clean percentage score
        score = round((1.0 - max(0.0, min(float(dist), 1.0))) * 100, 1)
        formatted.append({
            "id": meta["pmid"],
            "title": meta["title"],
            "abstract": doc,
            "relevance_score": score,
        })

    return sorted(formatted, key=lambda x: x["relevance_score"], reverse=True)
  except Exception as e:
    print(f"Search Error: {e}")
    return []


def generate_rag_answer(user_question):
  """Sends retrieved papers + user question to Groq AI to generate a response."""
  try:
    results = collection.query(query_texts=[user_question], n_results=3)
    if not results or not results["documents"][0]:
      return "Please run a search query first so I have research papers to read!"

    context = ""
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
      context += f"\n- Title: {meta['title']} (PMID: {meta['pmid']})\nAbstract: {doc}\n"

    prompt = f"""
        You are a clinical AI assistant. Answer the user's question accurately using ONLY the research papers provided below. Do not make up facts. Cite the PMIDs.
        
        Research Papers:
        {context}
        
        User Question: {user_question}
        """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"AI Generation Error: {e}"