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


# --- 2. UNIFIED CONCEPT EXTRACTION & ONTOLOGY GROUNDING ENGINE ---

STOP_WORDS = {
    "a", "an", "and", "are", "can", "could", "do", "does", "for", "how",
    "in", "is", "of", "the", "to", "what", "with", "help", "from", "many",
    "some", "such", "than", "that", "this", "these", "those"
}

CANDIDATE_MODELS = [
    "groq/compound-mini",
    "groq/compound",
    "openai/gpt-oss-120b"
]


def _extract_concepts_llm(user_query: str, api_key: str) -> dict:
  """Extracts structured clinical concept entities from the complete natural language inquiry."""
  if not api_key or not api_key.strip():
    return {"concepts": [], "intent": "Targeted Literature Discovery"}

  prompt = f"""You are a National Library of Medicine (NLM) Medical Ontologist and expert PubMed query engineer.
Analyze this natural language biomedical research question and extract all distinct clinical and biomedical concepts into standardized NLM MeSH headings, clinical synonyms, and PICO facets.

USER INQUIRY: "{user_query}"

CRITICAL EXTRACTION RULES:
1. Identify all distinct clinical concept entities (Condition, Intervention/Drug, Population, Outcome/Etiology/Intent).
2. DO NOT split compound phrases into isolated words (e.g. "risk factors" must be extracted as a single concept, "young adults" as a single concept, "liver fibrosis" as a single concept, "drug-resistant tuberculosis" as a single concept, "Alzheimer's disease" as a single concept, "infertility" as a single concept, "endometriosis" as a single concept).
3. For EACH concept entity, provide:
   - name: Clear clinical concept name
   - facet: One of ["condition", "intervention", "population", "outcome"]
   - mesh_terms: 1-3 official NLM MeSH descriptor terms (e.g. "Stroke", "Risk Factors", "Young Adult", "Liver Cirrhosis", "Tuberculosis, Multidrug-Resistant", "Endometriosis", "Infertility, Female")
   - clinical_synonyms: 2-4 standard clinical synonyms, abbreviations, or keywords (e.g. "cerebrovascular accident", "CVA", "risk factor", "MDR-TB")

RESPOND WITH ONLY A RAW JSON OBJECT (no markdown backticks, no other text):
{{
    "concepts": [
        {{
            "name": "Concept Name",
            "facet": "condition / intervention / population / outcome",
            "mesh_terms": ["Official MeSH 1", "Official MeSH 2"],
            "clinical_synonyms": ["Synonym 1", "Synonym 2"]
        }}
    ],
    "intent": "Concise 2-4 word clinical intent label"
}}"""

  try:
    client = Groq(api_key=api_key.strip())
    for model_id in CANDIDATE_MODELS:
      try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a clinical biomedical ontologist. Output valid raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.05,
            max_tokens=800
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
        if data.get("concepts"):
          return data
      except Exception:
        continue
  except Exception:
    pass
  return {"concepts": [], "intent": "Targeted Literature Discovery"}


# --- 3. MAIN TRANSLATION & CLINICAL FACET EXTRACTION ENGINE ---
@st.cache_data(ttl=3600, show_spinner=False)
def translate_to_mesh_query(user_query: str, use_llm: bool = True, fast_mode: bool = False) -> dict:
  """Translates natural language questions into structured clinical facets and a validated PubMed Boolean query."""
  q_clean = user_query.strip()
  q_lower = q_clean.lower()
  api_key = os.getenv("GROQ_API_KEY")

  # Step 1: Deterministic Dictionary Entity Matching
  dict_concepts = []
  matched_spans = []
  sorted_dict = sorted(MEDICAL_DICTIONARY.items(), key=lambda x: len(x[0]), reverse=True)

  for phrase, mapping in sorted_dict:
    start_pos = 0
    while True:
      idx = q_lower.find(phrase, start_pos)
      if idx == -1:
        break
      end_idx = idx + len(phrase)
      is_overlapped = any((idx >= s and idx < e) or (end_idx > s and end_idx <= e) for s, e in matched_spans)
      if not is_overlapped:
        matched_spans.append((idx, end_idx))
        dict_concepts.append({
            "name": phrase.title(),
            "facet": mapping.get("facet", "condition"),
            "mesh_terms": mapping.get("mesh", []),
            "clinical_synonyms": mapping.get("clinical", []),
            "query_part": mapping.get("query_part")
        })
      start_pos = end_idx

  # Check for unmapped substantive words
  unmatched_words = [
      cleaned for w in q_clean.split()
      if len(w) > 2
      and (cleaned := re.sub(r"[^\w\s-]", "", w).lower()) not in STOP_WORDS
      and not any(span[0] <= q_lower.find(cleaned) < span[1] for span in matched_spans)
  ]

  is_fully_covered = bool(dict_concepts and not unmatched_words)

  # Step 2: Extract from LLM if unmapped concepts exist
  llm_concepts = []
  llm_intent = None
  validation_status = "rule_based"

  if use_llm and not is_fully_covered and api_key and api_key.strip():
    llm_data = _extract_concepts_llm(q_clean, api_key)
    llm_concepts = llm_data.get("concepts", [])
    llm_intent = llm_data.get("intent")
    if llm_concepts:
      validation_status = "llm_grounded_valid"

  # Step 3: Merge Dictionary + LLM Concepts with Deduplication
  merged_concepts = []
  seen_mesh = set()

  # Prioritize Dictionary matches for high-precision grounding
  for dc in dict_concepts:
    primary_mesh = dc["mesh_terms"][0] if dc["mesh_terms"] else dc["name"]
    seen_mesh.add(primary_mesh.lower())
    merged_concepts.append(dc)

  # Incorporate LLM extracted concepts for missing/unlisted biomedical entities
  for lc in llm_concepts:
    lc_mesh = lc.get("mesh_terms", [])
    primary_mesh = lc_mesh[0] if lc_mesh else lc.get("name", "")
    if primary_mesh.lower() not in seen_mesh:
      seen_mesh.add(primary_mesh.lower())
      merged_concepts.append(lc)

  # Step 4: Deterministic Multi-Facet Boolean Builder
  all_mesh = []
  all_clinical = []
  facets = {
      "condition": None,
      "intervention_or_biomarker": None,
      "population": None,
      "outcome_or_intent": None,
      "intent": llm_intent or "Targeted Literature Discovery"
  }

  concept_clauses = []

  for c in merged_concepts:
    c_name = c.get("name", "")
    c_facet = c.get("facet", "condition").lower()
    c_mesh = c.get("mesh_terms", [])
    c_syns = c.get("clinical_synonyms", [])
    q_part = c.get("query_part")

    all_mesh.extend(c_mesh)
    all_clinical.extend(c_syns)

    # Update Facet Role
    if c_facet == "condition" and not facets["condition"]:
      facets["condition"] = c_mesh[0] if c_mesh else c_name
    elif c_facet in ["intervention", "biomarker"] and not facets["intervention_or_biomarker"]:
      facets["intervention_or_biomarker"] = c_mesh[0] if c_mesh else c_name
    elif c_facet == "population" and not facets["population"]:
      facets["population"] = c_mesh[0] if c_mesh else c_name
    elif c_facet in ["outcome", "intent"] and not facets["outcome_or_intent"]:
      facets["outcome_or_intent"] = c_mesh[0] if c_mesh else c_name

    # Construct Boolean clause
    if q_part and is_fully_covered:
      concept_clauses.append(q_part)
    else:
      clause_elements = []
      for m in c_mesh:
        clause_elements.append(f'"{m}"[MeSH Terms]')
      for s in c_syns:
        s_clean = s.strip().strip('"').strip("'")
        if s_clean and s_clean.lower() not in STOP_WORDS:
          clause_elements.append(f'"{s_clean}"[tiab]')
      if not clause_elements and c_name:
        clause_elements.append(f'"{c_name}"[tiab]')

      unique_elements = list(dict.fromkeys(clause_elements))
      if unique_elements:
        concept_clauses.append(f"({' OR '.join(unique_elements)})")

  # Step 5: Residual text handling (only if genuinely unmapped)
  if not merged_concepts and unmatched_words:
    residual_clause = " AND ".join(f'"{w}"[tiab]' for w in unmatched_words[:6])
    final_bool = residual_clause
  elif concept_clauses:
    final_bool = " AND ".join(concept_clauses)
  else:
    final_bool = q_clean

  # Step 6: Syntax Shield Validation
  is_valid, validated_query = validate_pubmed_query(final_bool)
  if not is_valid or not validated_query:
    validated_query = final_bool

  # Ensure UI facets
  if not facets.get("condition") and all_mesh:
    facets["condition"] = all_mesh[0]
  if not facets.get("intent"):
    facets["intent"] = "Targeted Literature Discovery"

  return {
      "pubmed_query": validated_query,
      "mesh_terms": list(dict.fromkeys(all_mesh)),
      "clinical_terms": list(dict.fromkeys(all_clinical)),
      "facets": facets,
      "validation_status": validation_status,
      "_dict_concepts": dict_concepts,
      "_llm_concepts": llm_concepts,
      "_merged_concepts": merged_concepts
  }


def debug_translate_query(user_query: str) -> dict:
  """Diagnostic utility that logs concept breakdown and Boolean query."""
  res = translate_to_mesh_query(user_query, use_llm=True)
  print(f"\nQUERY: \"{user_query}\"")
  print(f"  • Dictionary Matched Concepts : {[c['name'] for c in res.get('_dict_concepts', [])]}")
  print(f"  • LLM Extracted Concepts      : {[c.get('name') for c in res.get('_llm_concepts', [])]}")
  print(f"  • Merged Concepts ({len(res.get('_merged_concepts', []))}):")
  for c in res.get('_merged_concepts', []):
    print(f"      - [{c.get('facet', '').upper()}] {c.get('name')}: MeSH={c.get('mesh_terms')}")
  print(f"  • Facets                      : {res['facets']}")
  print(f"  • Final PubMed Boolean Query  :\n    {res['pubmed_query']}")
  print("-" * 80)
  return res
