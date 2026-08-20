from __future__ import annotations
import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Built-in medical concept mapping for instant, zero-latency clinical ontology resolution
MEDICAL_DICTIONARY = {
    "sugar disease": {
        "mesh": ["Diabetes Mellitus", "Diabetic Nephropathies"],
        "clinical": ["Diabetes Mellitus Type 2", "Diabetic Kidney Disease"],
        "query": (
            '("Diabetic Nephropathies"[MeSH Terms] OR "diabetic kidney'
            ' disease"[tiab] OR "diabetic nephropathy"[tiab])'
        ),
    },
    "kidney damage": {
        "mesh": ["Renal Insufficiency", "Kidney Diseases"],
        "clinical": ["Chronic Kidney Disease", "Renal Impairment"],
        "query": (
            '("Renal Insufficiency"[MeSH Terms] OR "kidney damage"[tiab] OR'
            ' "chronic kidney disease"[tiab])'
        ),
    },
    "lung cancer": {
        "mesh": ["Lung Neoplasms", "Carcinoma, Non-Small-Cell Lung"],
        "clinical": ["Non-Small Cell Lung Cancer (NSCLC)", "Thoracic Oncology"],
        "query": (
            '("Lung Neoplasms"[MeSH Terms] OR "non-small cell lung'
            ' cancer"[tiab] OR "NSCLC"[tiab])'
        ),
    },
    "immunotherapy": {
        "mesh": ["Immunotherapy", "Immune Checkpoint Inhibitors"],
        "clinical": ["PD-1 / PD-L1 Blockade", "CTLA-4 Inhibitors"],
        "query": (
            '("Immunotherapy"[MeSH Terms] OR "immune checkpoint'
            ' inhibitors"[tiab] OR "pembrolizumab"[tiab])'
        ),
    },
    "pediatric asthma": {
        "mesh": ["Asthma", "Child", "Pediatrics"],
        "clinical": ["Childhood Bronchial Asthma", "Pediatric Exacerbation"],
        "query": (
            '("Asthma"[MeSH Terms] AND ("Child"[MeSH Terms] OR'
            ' "Pediatrics"[MeSH Terms]))'
        ),
    },
    "alzheimer": {
        "mesh": ["Alzheimer Disease", "Biomarkers", "Amyloid beta-Peptides"],
        "clinical": ["Tau Protein", "Neurodegeneration Biomarkers", "Early Stage AD"],
        "query": (
            '("Alzheimer Disease"[MeSH Terms] AND ("Biomarkers"[MeSH Terms] OR'
            ' "amyloid"[tiab] OR "tau"[tiab]))'
        ),
    },
    "heart attack": {
        "mesh": ["Myocardial Infarction", "Coronary Artery Disease"],
        "clinical": ["Acute Coronary Syndrome", "Myocardial Ischemia"],
        "query": (
            '("Myocardial Infarction"[MeSH Terms] OR "acute myocardial'
            ' infarction"[tiab] OR "heart attack"[tiab])'
        ),
    },
    "old people": {
        "mesh": ["Aged", "Geriatrics"],
        "clinical": ["Elderly Patients", "Geriatric Population"],
        "query": '("Aged"[MeSH Terms] OR "elderly"[tiab] OR "geriatric"[tiab])',
    },
}


def translate_to_mesh_query(user_query: str) -> dict:
  """Translates user natural language into standardized MeSH ontology and Boolean queries."""
  api_key = os.getenv("GROQ_API_KEY")
  q_lower = user_query.lower()

  matched_mesh = []
  matched_clinical = []
  matched_query_parts = []

  # Step A: Fast rule-based dictionary check
  for phrase, mapping in MEDICAL_DICTIONARY.items():
    if phrase in q_lower:
      matched_mesh.extend(mapping["mesh"])
      matched_clinical.extend(mapping["clinical"])
      matched_query_parts.append(mapping["query"])

  # Step B: LLM Dynamic Translation
  if api_key and api_key.strip():
    prompt = f"""You are a National Library of Medicine (NLM) Medical Ontologist.
Convert this clinical query into official MeSH descriptors, clinical synonyms, and a valid PubMed Boolean search string.
Query: "{user_query}"

Respond with ONLY a JSON object:
{{
    "mesh_terms": ["MeSH Heading 1", "MeSH Heading 2"],
    "clinical_terms": ["Clinical Synonym 1", "Clinical Synonym 2"],
    "pubmed_query": "(term1[MeSH Terms] OR term1[tiab]) AND (term2[MeSH Terms] OR term2[tiab])"
}}
"""
    try:
      client = Groq(api_key=api_key.strip())
      candidate_models = [
          "llama-3.3-70b-versatile",
          "llama-3.1-8b-instant",
      ]

      for m in candidate_models:
        try:
          response = client.chat.completions.create(
              model=m,
              messages=[{"role": "user", "content": prompt}],
              response_format={"type": "json_object"},
              temperature=0.1,
              max_tokens=300,
          )
          data = json.loads(response.choices[0].message.content)
          if data.get("mesh_terms"):
            matched_mesh.extend(data["mesh_terms"])
          if data.get("clinical_terms"):
            matched_clinical.extend(data["clinical_terms"])
          if data.get("pubmed_query") and not matched_query_parts:
            matched_query_parts.append(data["pubmed_query"])
          break
        except Exception:
          continue
    except Exception:
      pass

  # Step C: Fallbacks if both LLM and dictionary returned empty
  if not matched_mesh:
    matched_mesh = [
        "Clinical Medicine",
        "Therapeutics",
        "Biomedical Research",
    ]
  if not matched_clinical:
    matched_clinical = ["Evidence-Based Practice", "Pathophysiology"]

  final_query = (
      " AND ".join(matched_query_parts) if matched_query_parts else user_query
  )

  return {
      "pubmed_query": final_query,
      "mesh_terms": list(dict.fromkeys(matched_mesh)),
      "clinical_terms": list(dict.fromkeys(matched_clinical)),
  }