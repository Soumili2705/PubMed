from __future__ import annotations
import json
import os
import re
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

load_dotenv()

# --- 1. COMPREHENSIVE MEDICAL & MESH ONTOLOGY KNOWLEDGE BASE ---
# High-precision concept mappings grounded in NLM MeSH headings and standard clinical terminology.
MEDICAL_DICTIONARY: dict[str, dict] = {
    # Neurodegenerative & Mental Health
    "alzheimer": {
        "mesh": ["Alzheimer Disease", "Biomarkers", "Amyloid beta-Peptides", "tau Proteins"],
        "clinical": ["Early Stage Alzheimer Disease", "Plasma p-tau217", "Neurodegeneration Biomarkers"],
        "facet": "condition",
        "query_part": '("Alzheimer Disease"[MeSH Terms] OR "alzheimers disease"[tiab] OR "alzheimer"[tiab])',
    },
    "parkinson": {
        "mesh": ["Parkinson Disease", "alpha-Synuclein", "Dopaminergic Neurons"],
        "clinical": ["Parkinson's Disease Progression", "Lewy Body", "Movement Disorders"],
        "facet": "condition",
        "query_part": '("Parkinson Disease"[MeSH Terms] OR "parkinsons disease"[tiab] OR "parkinson"[tiab])',
    },
    "dementia": {
        "mesh": ["Dementia", "Cognitive Dysfunction", "Neurocognitive Disorders"],
        "clinical": ["Mild Cognitive Impairment", "Vascular Dementia", "Frontotemporal Dementia"],
        "facet": "condition",
        "query_part": '("Dementia"[MeSH Terms] OR "cognitive impairment"[tiab] OR "dementia"[tiab])',
    },
    # Metabolic & Renal
    "sugar disease": {
        "mesh": ["Diabetes Mellitus", "Diabetic Nephropathies", "Glycated Hemoglobin"],
        "clinical": ["Type 2 Diabetes Mellitus", "Diabetic Kidney Disease", "Hyperglycemia"],
        "facet": "condition",
        "query_part": '("Diabetes Mellitus, Type 2"[MeSH Terms] OR "diabetic nephropathies"[MeSH Terms] OR "diabetic kidney disease"[tiab])',
    },
    "diabetes": {
        "mesh": ["Diabetes Mellitus", "Diabetic Nephropathies", "Insulin Resistance"],
        "clinical": ["Type 2 Diabetes Mellitus", "Diabetic Kidney Disease", "HbA1c"],
        "facet": "condition",
        "query_part": '("Diabetes Mellitus"[MeSH Terms] OR "diabetes mellitus"[tiab] OR "diabetic"[tiab])',
    },
    "kidney damage": {
        "mesh": ["Renal Insufficiency, Chronic", "Kidney Diseases", "Glomerular Filtration Rate"],
        "clinical": ["Chronic Kidney Disease (CKD)", "Renal Impairment", "End-Stage Renal Disease"],
        "facet": "condition",
        "query_part": '("Renal Insufficiency, Chronic"[MeSH Terms] OR "chronic kidney disease"[tiab] OR "kidney damage"[tiab] OR "renal impairment"[tiab])',
    },
    "chronic kidney disease": {
        "mesh": ["Renal Insufficiency, Chronic", "Kidney Failure, Chronic"],
        "clinical": ["CKD Stage 3-5", "Estimated GFR Decline", "Albuminuria"],
        "facet": "condition",
        "query_part": '("Renal Insufficiency, Chronic"[MeSH Terms] OR "chronic kidney disease"[tiab] OR "CKD"[tiab])',
    },
    # Oncology
    "lung cancer": {
        "mesh": ["Lung Neoplasms", "Carcinoma, Non-Small-Cell Lung", "Small Cell Lung Carcinoma"],
        "clinical": ["Non-Small Cell Lung Cancer (NSCLC)", "Thoracic Oncology", "EGFR Mutation"],
        "facet": "condition",
        "query_part": '("Lung Neoplasms"[MeSH Terms] OR "non-small cell lung cancer"[tiab] OR "NSCLC"[tiab] OR "lung cancer"[tiab])',
    },
    "breast cancer": {
        "mesh": ["Breast Neoplasms", "Receptors, Estrogen", "ErbB-2 Receptor"],
        "clinical": ["Triple-Negative Breast Cancer (TNBC)", "HER2-Positive Breast Cancer", "BRCA Mutation"],
        "facet": "condition",
        "query_part": '("Breast Neoplasms"[MeSH Terms] OR "breast cancer"[tiab] OR "triple negative breast cancer"[tiab])',
    },
    "colorectal cancer": {
        "mesh": ["Colorectal Neoplasms", "Microsatellite Instability"],
        "clinical": ["Colon Carcinoma", "MSI-High Colorectal Cancer", "KRAS Mutation"],
        "facet": "condition",
        "query_part": '("Colorectal Neoplasms"[MeSH Terms] OR "colorectal cancer"[tiab] OR "colon cancer"[tiab])',
    },
    "melanoma": {
        "mesh": ["Melanoma", "Proto-Oncogene Proteins B-raf"],
        "clinical": ["Advanced Cutaneous Melanoma", "BRAF V600E Mutation", "Metastatic Melanoma"],
        "facet": "condition",
        "query_part": '("Melanoma"[MeSH Terms] OR "melanoma"[tiab] OR "cutaneous melanoma"[tiab])',
    },
    # Cardiovascular & Respiratory
    "heart attack": {
        "mesh": ["Myocardial Infarction", "Coronary Artery Disease", "Troponin"],
        "clinical": ["Acute Myocardial Infarction (AMI)", "Acute Coronary Syndrome", "ST-Elevation MI"],
        "facet": "condition",
        "query_part": '("Myocardial Infarction"[MeSH Terms] OR "acute myocardial infarction"[tiab] OR "heart attack"[tiab])',
    },
    "heart failure": {
        "mesh": ["Heart Failure", "Natriuretic Peptide, Brain", "Ventricular Dysfunction"],
        "clinical": ["HFrEF", "HFpEF", "Congestive Heart Failure", "Cardiomyopathy"],
        "facet": "condition",
        "query_part": '("Heart Failure"[MeSH Terms] OR "heart failure"[tiab] OR "HFrEF"[tiab] OR "HFpEF"[tiab])',
    },
    "pediatric asthma": {
        "mesh": ["Asthma", "Child", "Pediatrics", "Bronchodilator Agents"],
        "clinical": ["Childhood Bronchial Asthma", "Acute Pediatric Exacerbation", "Inhaled Corticosteroids"],
        "facet": "condition",
        "query_part": '("Asthma"[MeSH Terms] OR "asthma"[tiab]) AND ("Child"[MeSH Terms] OR "Pediatrics"[MeSH Terms] OR "pediatric"[tiab] OR "children"[tiab])',
    },
    "asthma": {
        "mesh": ["Asthma", "Bronchial Hyperreactivity", "Anti-Asthmatic Agents"],
        "clinical": ["Bronchial Asthma", "Airway Inflammation", "Eosinophilic Asthma"],
        "facet": "condition",
        "query_part": '("Asthma"[MeSH Terms] OR "asthma"[tiab] OR "bronchial asthma"[tiab])',
    },
    # Interventions, Biomarkers & Diagnostics
    "immunotherapy": {
        "mesh": ["Immunotherapy", "Immune Checkpoint Inhibitors", "Programmed Cell Death 1 Receptor"],
        "clinical": ["PD-1 / PD-L1 Inhibitors", "Pembrolizumab", "Nivolumab", "CTLA-4 Blockade"],
        "facet": "intervention",
        "query_part": '("Immunotherapy"[MeSH Terms] OR "immune checkpoint inhibitors"[MeSH Terms] OR "checkpoint inhibitor"[tiab] OR "pembrolizumab"[tiab] OR "nivolumab"[tiab])',
    },
    "immune checkpoint inhibitors": {
        "mesh": ["Immune Checkpoint Inhibitors", "Immunotherapy"],
        "clinical": ["PD-1 / PD-L1 Inhibitors", "CTLA-4 Blockade", "Checkpoint Blockade"],
        "facet": "intervention",
        "query_part": '("Immune Checkpoint Inhibitors"[MeSH Terms] OR "immune checkpoint inhibitor"[tiab] OR "PD-1 inhibitor"[tiab] OR "PD-L1 inhibitor"[tiab] OR "checkpoint blockade"[tiab])',
    },
    "car-t": {
        "mesh": ["Immunotherapy, Adoptive", "Receptors, Chimeric Antigen"],
        "clinical": ["CAR-T Cell Therapy", "Chimeric Antigen Receptor T-cell", "Cellular Immunotherapy"],
        "facet": "intervention",
        "query_part": '("Receptors, Chimeric Antigen"[MeSH Terms] OR "CAR-T"[tiab] OR "chimeric antigen receptor"[tiab])',
    },
    "biomarker": {
        "mesh": ["Biomarkers", "Biomarkers, Pharmacological", "Early Diagnosis"],
        "clinical": ["Plasma Biomarkers", "Diagnostic Sensitivity", "Molecular Assays"],
        "facet": "intervention",
        "query_part": '("Biomarkers"[MeSH Terms] OR "biomarkers"[tiab] OR "biomarker"[tiab] OR "plasma biomarker"[tiab])',
    },
    "p-tau217": {
        "mesh": ["Biomarkers", "tau Proteins"],
        "clinical": ["Plasma p-tau217", "Phosphorylated tau 217", "Blood-Based Biomarker"],
        "facet": "intervention",
        "query_part": '("p-tau217"[tiab] OR "phosphorylated tau 217"[tiab] OR "plasma p-tau217"[tiab])',
    },
    "amyloid pet": {
        "mesh": ["Amyloid beta-Peptides", "Positron-Emission Tomography"],
        "clinical": ["Amyloid PET Imaging", "Amyloid Imaging", "PET Biomarker"],
        "facet": "intervention",
        "query_part": '("Amyloid beta-Peptides"[MeSH Terms] OR "amyloid PET"[tiab] OR "amyloid imaging"[tiab])',
    },
    "early detection": {
        "mesh": ["Early Diagnosis", "Early Detection of Cancer", "Mass Screening"],
        "clinical": ["Preclinical Detection", "Early-Stage Screening", "Diagnostic Accuracy"],
        "facet": "outcome",
        "query_part": '("Early Diagnosis"[MeSH Terms] OR "early detection"[tiab] OR "early diagnosis"[tiab] OR "screening"[tiab])',
    },
    "tests": {
        "mesh": ["Diagnostic Tests, Routine", "Biomarkers"],
        "clinical": ["Diagnostic Testing", "Laboratory Assays"],
        "facet": "intervention",
        "query_part": '("Diagnostic Tests, Routine"[MeSH Terms] OR "Biomarkers"[MeSH Terms] OR "tests"[tiab] OR "diagnostic assay"[tiab])',
    },
    "causes": {
        "mesh": ["Etiology", "Causality", "Risk Factors"],
        "clinical": ["Etiology", "Underlying Causes", "Risk Factors"],
        "facet": "outcome",
        "query_part": '("Etiology"[MeSH Terms] OR "Risk Factors"[MeSH Terms] OR "causes"[tiab] OR "etiology"[tiab] OR "risk factors"[tiab])',
    },
    "preclinical": {
        "mesh": ["Early Diagnosis"],
        "clinical": ["Preclinical Detection", "Preclinical Alzheimer Disease"],
        "facet": "outcome",
        "query_part": '("Early Diagnosis"[MeSH Terms] OR preclinical[tiab] OR "preclinical detection"[tiab])',
    },
    "gut microbiome": {
        "mesh": ["Gastrointestinal Microbiome"],
        "clinical": ["Gut Microbiota", "Intestinal Microbiome", "Microbiome Dysbiosis"],
        "facet": "intervention",
        "query_part": '("Gastrointestinal Microbiome"[MeSH Terms] OR "gut microbiome"[tiab] OR "gut microbiota"[tiab])',
    },
    "depression": {
        "mesh": ["Depressive Disorder"],
        "clinical": ["Major Depressive Disorder", "Depressive Symptoms", "Clinical Depression"],
        "facet": "condition",
        "query_part": '("Depressive Disorder"[MeSH Terms] OR depression[tiab] OR "major depressive disorder"[tiab])',
    },
    "relapse": {
        "mesh": ["Recurrence"],
        "clinical": ["Depression Relapse", "Disease Recurrence", "Relapse Prediction"],
        "facet": "outcome",
        "query_part": '("Recurrence"[MeSH Terms] OR relapse[tiab] OR recurrence[tiab] OR predict*[tiab])',
    },
    "crispr": {
        "mesh": ["CRISPR-Cas Systems", "Gene Editing", "Genetic Therapy"],
        "clinical": ["CRISPR-Cas9 Gene Editing", "Targeted Mutagenesis", "In Vivo Gene Therapy"],
        "facet": "intervention",
        "query_part": '("CRISPR-Cas Systems"[MeSH Terms] OR "CRISPR"[tiab] OR "gene editing"[tiab])',
    },
    # Populations
    "young people": {
        "mesh": ["Young Adult", "Adolescent"],
        "clinical": ["Young Adults", "Young Patients", "Early-Onset Cohort"],
        "facet": "population",
        "query_part": '("Young Adult"[MeSH Terms] OR "young people"[tiab] OR "young adult"[tiab] OR "young adults"[tiab])',
    },
    "young adults": {
        "mesh": ["Young Adult"],
        "clinical": ["Young Adults", "Early-Onset Cohort"],
        "facet": "population",
        "query_part": '("Young Adult"[MeSH Terms] OR "young adult"[tiab] OR "young adults"[tiab])',
    },
    "old people": {
        "mesh": ["Aged", "Geriatrics", "Aged, 80 and over"],
        "clinical": ["Elderly Patients", "Geriatric Cohort", "Aging Population"],
        "facet": "population",
        "query_part": '("Aged"[MeSH Terms] OR "elderly"[tiab] OR "geriatric"[tiab] OR "older adults"[tiab])',
    },
    "elderly": {
        "mesh": ["Aged", "Geriatrics", "Aged, 80 and over"],
        "clinical": ["Elderly Patients", "Geriatric Cohort", "Older Adults"],
        "facet": "population",
        "query_part": '("Aged"[MeSH Terms] OR "elderly"[tiab] OR "geriatric"[tiab] OR "older patients"[tiab])',
    },
    "children": {
        "mesh": ["Child", "Pediatrics", "Infant"],
        "clinical": ["Pediatric Population", "Childhood Cohort", "Adolescents"],
        "facet": "population",
        "query_part": '("Child"[MeSH Terms] OR "Pediatrics"[MeSH Terms] OR "pediatric"[tiab] OR "children"[tiab])',
    },
    "pediatric": {
        "mesh": ["Child", "Pediatrics", "Infant"],
        "clinical": ["Pediatric Patients", "Childhood", "Pediatric Guidelines"],
        "facet": "population",
        "query_part": '("Child"[MeSH Terms] OR "Pediatrics"[MeSH Terms] OR "pediatric"[tiab] OR "childhood"[tiab])',
    },
}


# --- 2. LIGHTWEIGHT QUERY VALIDATOR ---
def validate_pubmed_query(query: str) -> tuple[bool, str]:
  """Validates a generated PubMed Boolean query string for structural correctness.

  Checks:
  - Balanced parentheses
  - Non-empty content
  - No illegal consecutive operators ('AND AND', 'OR OR', 'AND OR', etc.)
  - No leading/trailing Boolean operators
  - Valid PubMed field tags like [MeSH Terms], [tiab], [ti], [tw]

  Returns: (is_valid: bool, sanitized_or_fallback_query: str)
  """
  if not query or not query.strip():
    return False, ""

  q = query.strip()

  # Normalize single quotes to double quotes
  q = re.sub(r"\'([^\']+)\'", r'"\1"', q)

  # 1. Balanced parentheses check
  if q.count("(") != q.count(")"):
    return False, q

  # 2. Check for empty parentheses like () or ( )
  if re.search(r"\(\s*\)", q):
    q = re.sub(r"\(\s*\)", "", q).strip()

  # 3. Clean consecutive operators
  q = re.sub(r"\bAND\s+AND\b", "AND", q, flags=re.IGNORECASE)
  q = re.sub(r"\bOR\s+OR\b", "OR", q, flags=re.IGNORECASE)
  q = re.sub(r"\bAND\s+OR\b", "AND", q, flags=re.IGNORECASE)
  q = re.sub(r"\bOR\s+AND\b", "AND", q, flags=re.IGNORECASE)

  # 4. Remove leading/trailing operators
  q = re.sub(r"^(AND|OR|NOT)\s+", "", q, flags=re.IGNORECASE).strip()
  q = re.sub(r"\s+(AND|OR|NOT)$", "", q, flags=re.IGNORECASE).strip()

  # 5. Ensure at least one substantive search term exists
  cleaned_terms = re.sub(r"\[[a-zA-Z\s]+\]", "", q)
  cleaned_terms = re.sub(r"[\(\)\"\']", "", cleaned_terms)
  tokens = [
      w for w in cleaned_terms.split() if w.upper() not in ["AND", "OR", "NOT"]
  ]

  if len(tokens) == 0:
    return False, query

  return True, q


STOP_WORDS = {
    "a", "an", "and", "are", "can", "could", "do", "does", "for", "how",
    "in", "is", "of", "the", "to", "what", "with", "help", "from", "many",
    "some", "such", "than", "that", "this", "these", "those"
}


def build_boolean_from_facet_concepts(facet_groups: dict[str, list[dict]]) -> str:
  """Constructs a syntax-valid PubMed Boolean query where:

  - Concepts and clinical synonyms within the same semantic facet are combined with OR.
  - Distinct required semantic facets (Condition, Biomarker/Intervention, Population, Outcome) are combined with AND.
  """
  facet_clauses = []
  facet_order = ["condition", "intervention", "population", "outcome"]

  for f in facet_order:
    items = facet_groups.get(f, [])
    if not items:
      continue

    clause_elements = []
    for item in items:
      if item.get("query_part"):
        clause_elements.append(item["query_part"])
      else:
        # 1. Official MeSH headings
        for m in item.get("mesh", []):
          clause_elements.append(f'"{m}"[MeSH Terms]')
        # 2. Standard clinical synonyms / phrases
        for c in item.get("clinical", []):
          c_clean = c.strip().strip('"').strip("'")
          if c_clean and c_clean.lower() not in STOP_WORDS:
            clause_elements.append(f'"{c_clean}"[tiab]')

    unique_elements = list(dict.fromkeys(clause_elements))
    if unique_elements:
      combined = " OR ".join(unique_elements)
      if not (combined.startswith("(") and combined.endswith(")")):
        combined = f"({combined})"
      facet_clauses.append(combined)

  if facet_clauses:
    return " AND ".join(facet_clauses)
  return ""


def _build_rule_based_query(user_query: str) -> tuple[str, list[str], list[str], dict, list[str]]:
  """Constructs a deterministic, MeSH-grounded Boolean query using the local medical dictionary."""
  q_lower = user_query.lower()
  matched_mesh = []
  matched_clinical = []
  
  facet_groups = {
      "condition": [],
      "intervention": [],
      "population": [],
      "outcome": [],
  }
  
  facets = {
      "condition": None,
      "intervention_or_biomarker": None,
      "population": None,
      "outcome_or_intent": None,
      "intent": None,
  }

  matched_spans = []
  # Longest phrase matching first to prevent sub-token duplication (e.g. 'pediatric asthma' vs 'asthma' + 'pediatric')
  sorted_dict = sorted(MEDICAL_DICTIONARY.items(), key=lambda x: len(x[0]), reverse=True)

  for phrase, mapping in sorted_dict:
    start_pos = 0
    while True:
      idx = q_lower.find(phrase, start_pos)
      if idx == -1:
        break
      end_idx = idx + len(phrase)
      # Check if this span overlaps with an already matched longer span
      is_overlapped = any(
          (idx >= s and idx < e) or (end_idx > s and end_idx <= e)
          for s, e in matched_spans
      )
      if not is_overlapped:
        matched_spans.append((idx, end_idx))
        matched_mesh.extend(mapping["mesh"])
        matched_clinical.extend(mapping["clinical"])
        facet_type = mapping.get("facet", "condition")
        
        if facet_type in ["intervention", "biomarker"]:
          group_key = "intervention"
        elif facet_type == "population":
          group_key = "population"
        elif facet_type == "outcome":
          group_key = "outcome"
        else:
          group_key = "condition"

        facet_groups[group_key].append({
            "name": phrase.title(),
            "mesh": mapping.get("mesh", []),
            "clinical": mapping.get("clinical", []),
            "query_part": mapping.get("query_part"),
        })

        if group_key == "condition" and not facets["condition"]:
          facets["condition"] = mapping["mesh"][0] if mapping.get("mesh") else phrase.title()
        elif group_key == "intervention" and not facets["intervention_or_biomarker"]:
          facets["intervention_or_biomarker"] = mapping["mesh"][0] if mapping.get("mesh") else phrase.title()
        elif group_key == "population" and not facets["population"]:
          facets["population"] = mapping["clinical"][0] if mapping.get("clinical") else phrase.title()
        elif group_key == "outcome" and not facets["outcome_or_intent"]:
          facets["outcome_or_intent"] = mapping["clinical"][0] if mapping.get("clinical") else phrase.title()
      start_pos = end_idx

  stop_words = {
      "a", "an", "and", "are", "can", "could", "do", "does", "for", "how",
      "in", "is", "of", "the", "to", "what", "with", "help", "from", "many",
      "some", "such", "than", "that", "this", "these", "those",
  }

  # Identify residual words not covered by the medical dictionary
  unmatched_words = [
      cleaned for w in user_query.split()
      if len(w) > 2
      and (cleaned := re.sub(r"[^\w\s-]", "", w).lower()) not in stop_words
      and not any(span[0] <= q_lower.find(cleaned) < span[1] for span in matched_spans)
  ]

  # Generate Boolean query directly from normalized facet concepts (Residual words are NOT appended)
  final_bool = build_boolean_from_facet_concepts(facet_groups)

  if not final_bool:
    clean_words = [
        cleaned for word in user_query.split()
        if len(word) > 2
        and (cleaned := re.sub(r"[^\w\s-]", "", word).lower()) not in stop_words
    ]
    if clean_words:
      final_bool = " AND ".join(f'"{w}"[tiab]' for w in clean_words[:6])
    else:
      final_bool = user_query

  return final_bool, matched_mesh, matched_clinical, facets, unmatched_words


# --- 3. MAIN TRANSLATION & CLINICAL FACET EXTRACTION ENGINE ---
@st.cache_data(ttl=3600, show_spinner=False)
def translate_to_mesh_query(user_query: str, use_llm: bool = True, fast_mode: bool = False) -> dict:
  """Translates natural language questions into structured clinical facets and a validated PubMed Boolean query.

  PICO/Clinical Facets Extracted:
  - condition: primary pathology or disease
  - intervention_or_biomarker: therapeutic, assay, gene, or diagnostic tool
  - population: age cohort (pediatric, elderly, adult) or demographic
  - outcome_or_intent: primary endpoint (early detection, survival, guideline)

  Returns structured dictionary:
  {
      "pubmed_query": str,
      "mesh_terms": list[str],
      "clinical_terms": list[str],
      "facets": dict,
      "validation_status": str
  }
  """
  api_key = os.getenv("GROQ_API_KEY")
  q_clean = user_query.strip()

  # 1. Run deterministic rule-based mapping first
  rule_query, rule_mesh, rule_clinical, rule_facets, unmatched_words = _build_rule_based_query(q_clean)

  matched_mesh = list(rule_mesh)
  matched_clinical = list(rule_clinical)
  facets = dict(rule_facets)
  generated_pubmed_query = rule_query
  validation_status = "rule_based"

  # 2. Trigger LLM fallback if there are concepts not recognized by the dictionary
  should_call_llm = use_llm and bool(unmatched_words or not rule_mesh)

  if should_call_llm and api_key and api_key.strip():
    unresolved_str = ", ".join(unmatched_words) if unmatched_words else "None"
    prompt = f"""You are a National Library of Medicine (NLM) Medical Ontologist and expert PubMed query engineer.
Translate this natural language biomedical research question into standardized NLM MeSH headings, clinical synonyms, and an optimized PubMed Boolean search query.

USER INQUIRY: "{q_clean}"
UNRESOLVED CONCEPTS: {unresolved_str}

CRITICAL INSTRUCTIONS FOR BOOLEAN QUERY CONSTRUCTION:
1. Break down the inquiry into distinct clinical facets:
   - Condition / Disease: (e.g. "Alzheimer Disease"[MeSH Terms] OR "alzheimers disease"[tiab])
   - Intervention / Biomarker / Tool: (e.g. "Biomarkers"[MeSH Terms] OR "tau protein"[tiab] OR "p-tau217"[tiab])
   - Population (if explicitly requested, e.g. child, elderly, pregnant): (e.g. "Aged"[MeSH Terms] OR "elderly"[tiab])
   - Clinical Outcome / Intent (e.g. early detection, mortality, guideline): (e.g. "Early Diagnosis"[MeSH Terms] OR "screening"[tiab])
2. Combine synonyms WITHIN each facet using OR.
3. Combine ALL distinct clinical facets using AND. Do NOT omit any concept facet.
4. Enclose each facet in balanced parentheses.
5. Use recognized PubMed field tags: [MeSH Terms] and [tiab].
6. Do NOT add unrelated medical concepts or excessive terms that produce 0 results.
7. STRICT NO-EXPANSION RULE: DO NOT expand generic concepts (such as "risk factors", "treatments", "causes", "biomarkers") into specific unmentioned clinical diseases or drugs (e.g. do NOT invent "hypertension", "smoking", "diabetes", or "aspirin" when the inquiry asks generally for "risk factors" or "treatments"). Only provide the direct concept MeSH descriptor and direct synonyms (e.g. "risk factor", "risk determinant", "predictor", "therapy", "treatment", "therapeutic").

RESPOND WITH ONLY A JSON OBJECT:
{{
    "facets": {{
        "condition": "Primary Disease / Condition or null",
        "intervention_or_biomarker": "Intervention / Molecule / Assay or null",
        "population": "Population Cohort (e.g. Pediatric, Elderly, Adult) or null",
        "outcome_or_intent": "Clinical Endpoint / Outcome or null",
        "intent": "Concise 2-4 word intent label"
    }},
    "mesh_terms": ["Official MeSH Heading 1", "Official MeSH Heading 2"],
    "clinical_terms": ["Clinical Synonym 1", "Clinical Synonym 2"],
    "pubmed_query": "('Condition'[MeSH Terms] OR 'condition'[tiab]) AND ('Biomarker'[MeSH Terms] OR 'biomarker'[tiab])"
}}"""

    try:
      client = Groq(api_key=api_key.strip())
      candidate_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b"]

      for model_id in candidate_models:
        try:
          response = client.chat.completions.create(
              model=model_id,
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "You are a clinical biomedical ontologist. Output valid"
                          " JSON only. Construct precise, syntax-valid PubMed"
                          " Boolean queries."
                      ),
                  },
                  {"role": "user", "content": prompt},
              ],
              temperature=0.05,
              max_tokens=1500,
          )
          content = response.choices[0].message.content.strip()
          content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
          if "```" in content:
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
            content = re.sub(r"```$", "", content).strip()
          match = re.search(r'\{.*\}', content, re.DOTALL)
          if match:
            content = match.group(0)
          data = json.loads(content)

          # Extract data if valid
          if data.get("pubmed_query"):
            llm_query = data["pubmed_query"].strip()
            is_valid, sanitized = validate_pubmed_query(llm_query)

            if is_valid and len(sanitized) > 5:
              generated_pubmed_query = sanitized
              validation_status = "llm_grounded_valid"

              if data.get("mesh_terms"):
                matched_mesh.extend(data["mesh_terms"])
              if data.get("clinical_terms"):
                matched_clinical.extend(data["clinical_terms"])
              if data.get("facets") and isinstance(data["facets"], dict):
                for k, v in data["facets"].items():
                  if v and str(v).lower() != "null" and not facets.get(k):
                    facets[k] = str(v)
              break
        except Exception:
          continue
    except Exception:
      pass

  # 3. Final Validation & Sanity Check
  is_valid, final_query = validate_pubmed_query(generated_pubmed_query)
  if not is_valid or not final_query:
    final_query = rule_query
    validation_status = "fallback_rule_based"

  # Ensure default concepts exist for UI rendering (extract from query if dictionary missed)
  if not matched_mesh:
    words = [w.title() for w in re.findall(r'[a-zA-Z]{3,}', q_clean)]
    matched_mesh = words[:3] if words else ["Biomedical Research", "Clinical Medicine"]
  if not matched_clinical:
    matched_clinical = [f"{m} Therapy" for m in matched_mesh[:2]] if matched_mesh else ["Evidence-Based Medicine", "Clinical Outcomes"]

  # Infer missing facets if empty
  if not facets.get("condition") and matched_mesh:
    facets["condition"] = matched_mesh[0]
  if not facets.get("intent"):
    q_low = q_clean.lower()
    if any(w in q_low for w in ["biomarker", "early", "detect", "screen"]):
      facets["intent"] = "Early Detection & Biomarker Discovery"
    elif any(w in q_low for w in ["therapy", "treatment", "trial", "efficacy"]):
      facets["intent"] = "Therapeutic Efficacy & Clinical Trials"
    elif any(w in q_low for w in ["guideline", "management", "acute", "protocol"]):
      facets["intent"] = "Clinical Management & Guidelines"
    else:
      facets["intent"] = "Targeted Literature Discovery"

  return {
      "pubmed_query": final_query,
      "mesh_terms": list(dict.fromkeys(matched_mesh)),
      "clinical_terms": list(dict.fromkeys(matched_clinical)),
      "facets": facets,
      "validation_status": validation_status,
  }
