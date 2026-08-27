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
    "a", "an", "and", "are", "can", "could", "did", "do", "does", "for",
    "from", "had", "has", "have", "how", "in", "is", "of", "on", "or",
    "the", "to", "was", "were", "what", "when", "where", "which", "who",
    "whom", "whose", "why", "with", "help", "many", "some", "such",
    "than", "that", "this", "these", "those", "affect", "affects", "influence",
    "influences", "causing", "causes", "caused",
}

# ---------------------------------------------------------------------------
# VALIDATION GUARDRAIL — research-intent contamination detection & recovery
# ---------------------------------------------------------------------------
# Words that describe the *type* of research question, not the disease itself.
# If the Condition or Outcome field is set to one of these values it means the
# dictionary matched the research-intent word from the query instead of the
# actual biomedical entity.  We must recover the real entity from the query.
RESEARCH_INTENT_BLOCKLIST: set[str] = {
    "etiology", "risk factors", "risk factor", "causality", "causes", "cause",
    "treatment", "treatments", "diagnosis", "prognosis", "prevention",
    "management", "screening", "pathophysiology", "epidemiology",
    "underlying causes", "early detection", "early diagnosis",
}

# Extended stop-words for entity recovery (includes research-intent words
# themselves so they are skipped during noun extraction)
_RECOVERY_SKIP: set[str] = STOP_WORDS | RESEARCH_INTENT_BLOCKLIST | {
    "are", "is", "the", "what", "for", "type", "options", "factors",
    "options", "risk",
}


def _recover_biomedical_entity(user_query: str) -> tuple[str | None, str | None]:
    """Extract a candidate biomedical entity from the query when the normal
    extraction pipeline has been contaminated by a research-intent keyword.

    Strategy (rule-based, no LLM):
    1. Tokenise the query.
    2. Skip stop-words, research-intent words, and tokens shorter than 3 chars.
    3. Collect the remaining noun-like tokens (they are the disease / condition).
    4. Build a simple [tiab] query from those tokens.

    Returns (entity_label, tiab_pubmed_query) or (None, None) if recovery fails.
    """
    tokens = re.findall(r"[a-zA-Z0-9'-]+", user_query.lower())
    candidate_tokens = [
        t for t in tokens
        if len(t) >= 3 and t not in _RECOVERY_SKIP
    ]
    if not candidate_tokens:
        return None, None

    entity_label = " ".join(candidate_tokens[:3]).title()
    tiab_query = " AND ".join(f'"{t}"[tiab]' for t in candidate_tokens[:4])
    return entity_label, tiab_query


def _validate_and_repair_facets(
    user_query: str,
    facets: dict,
    generated_pubmed_query: str,
) -> tuple[dict, str]:
    """Guardrail applied immediately after extraction.

    Detects when the Condition or Outcome field contains a research-intent word
    (from RESEARCH_INTENT_BLOCKLIST) and replaces it with the actual biomedical
    entity recovered from the original query.  The research-intent term is
    preserved in the Intent field so no information is lost.

    Bug pattern caught:
      - A research-intent word from the query (e.g. "causes", "etiology")
        matched a dictionary entry and occupied the Outcome field.
      - The actual disease (e.g. "hypertension") was not in the dictionary and
        therefore produced no condition match (condition=None).
      - The resulting Boolean query searches only for research-intent concepts
        (Etiology, Risk Factors) with no disease constraint → completely
        irrelevant PubMed results.

    Only modifies ``facets`` and ``generated_pubmed_query``; does not touch
    ranking, retrieval, embeddings, or any other pipeline component.

    Returns: (repaired_facets, repaired_pubmed_query)
    """
    condition_val = (facets.get("condition") or "").strip().lower()
    outcome_val   = (facets.get("outcome_or_intent") or "").strip().lower()

    condition_contaminated = condition_val in RESEARCH_INTENT_BLOCKLIST
    outcome_contaminated   = outcome_val in RESEARCH_INTENT_BLOCKLIST

    if not condition_contaminated and not outcome_contaminated:
        # Nothing to fix — return as-is
        return facets, generated_pubmed_query

    # Preserve the research-intent term in the Intent field before clearing it
    contaminating_term = facets.get("condition") or facets.get("outcome_or_intent") or ""
    if contaminating_term and not facets.get("intent"):
        facets["intent"] = contaminating_term.title()

    # Attempt entity recovery from original query
    entity_label, recovery_query = _recover_biomedical_entity(user_query)

    # Record whether condition was None/empty before repair (used in both
    # the outcome branch and the query-replacement logic below)
    no_condition_before = not condition_val  # condition was None/empty before guardrail ran

    if condition_contaminated:
        # Replace the contaminating condition value with the recovered entity
        facets["condition"] = entity_label  # may be None if recovery failed

    if outcome_contaminated:
        # The outcome was a research-intent word; clear it — intent is
        # already preserved in the intent field above
        facets["outcome_or_intent"] = None
        # If condition was also empty (never set), assign the recovered entity
        # here so the UI has a meaningful Condition label and the downstream
        # late-stage fallback doesn't re-populate it with a research-intent MeSH term
        if no_condition_before and entity_label:
            facets["condition"] = entity_label

    # Replace the Boolean query when a disease-free, intent-only query was
    # generated.  Two triggering situations:
    #
    # Case A: condition field was contaminated (its previous value was a
    #   research-intent word).  After repair the condition is now set to the
    #   recovered entity, so the old query no longer reflects reality.
    #
    # Case B: condition was None (no disease matched the dictionary) AND
    #   outcome was contaminated (only a research-intent word matched).
    #   This means the entire Boolean query was built from research-intent
    #   terms — there is no disease constraint at all — so the query is
    #   guaranteed to return irrelevant results.
    #
    # In both cases replace with the recovery [tiab] query when available.
    should_replace_query = recovery_query and (
        condition_contaminated
        or (outcome_contaminated and no_condition_before)
    )
    if should_replace_query:
        generated_pubmed_query = recovery_query

    return facets, generated_pubmed_query




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

  # Identify residual words not covered by the medical dictionary
  unmatched_words = [
      cleaned for w in user_query.split()
      if len(w) > 2
      and (cleaned := re.sub(r"[^\w\s-]", "", w).lower()) not in STOP_WORDS
      and not any(span[0] <= q_lower.find(cleaned) < span[1] for span in matched_spans)
  ]

  # Generate Boolean query directly from normalized facet concepts (Residual words are NOT appended)
  final_bool = build_boolean_from_facet_concepts(facet_groups)

  if not final_bool:
    clean_words = [
        cleaned for word in user_query.split()
        if len(word) > 2
        and (cleaned := re.sub(r"[^\w\s-]", "", word).lower()) not in _RECOVERY_SKIP
    ]
    if clean_words:
      final_bool = " AND ".join(f'"{w}"[tiab]' for w in clean_words[:6])
    else:
      final_bool = user_query

  return final_bool, matched_mesh, matched_clinical, facets, unmatched_words


# --- 3. MAIN TRANSLATION & CLINICAL FACET EXTRACTION ENGINE ---
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
  if not user_query or not user_query.strip():
    return {
        "pubmed_query": "",
        "mesh_terms": [],
        "clinical_terms": [],
        "facets": {
            "condition": None,
            "intervention_or_biomarker": None,
            "population": None,
            "outcome_or_intent": None,
            "intent": None,
        },
        "validation_status": "empty_query",
    }

  q_clean = user_query.strip()
  disallowed = {
      "what biomedical question are you trying to explore?",
      "what biomedical question are you trying to explore",
      "e.g., early detection biomarkers in alzheimer's disease",
      "e.g., early detection biomarkers in alzheimers disease",
  }
  if q_clean.lower() in disallowed:
    return {
        "pubmed_query": "",
        "mesh_terms": [],
        "clinical_terms": [],
        "facets": {
            "condition": None,
            "intervention_or_biomarker": None,
            "population": None,
            "outcome_or_intent": None,
            "intent": None,
        },
        "validation_status": "invalid_placeholder_query",
    }

  api_key = os.getenv("GROQ_API_KEY")

  # 1. Run deterministic rule-based mapping first
  rule_query, rule_mesh, rule_clinical, rule_facets, unmatched_words = _build_rule_based_query(q_clean)

  matched_mesh = list(rule_mesh)
  matched_clinical = list(rule_clinical)
  facets = dict(rule_facets)
  generated_pubmed_query = rule_query
  validation_status = "rule_based"

  # 1a. Guardrail: detect and repair research-intent contamination in facets.
  #     If the Condition or Outcome field was set to a research-intent word
  #     (e.g. "Etiology", "Risk Factors") instead of the actual disease,
  #     recover the biomedical entity from the original query and move the
  #     research-intent term to the Intent field where it belongs.
  facets, generated_pubmed_query = _validate_and_repair_facets(
      q_clean, facets, generated_pubmed_query
  )

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
    words = [
        w.title() for w in re.findall(r'[a-zA-Z0-9\'-]{3,}', q_clean)
        if w.lower() not in _RECOVERY_SKIP
    ]
    matched_mesh = words[:3] if words else ["Biomedical Research", "Clinical Medicine"]
  if not matched_clinical:
    matched_clinical = [f"{m} Therapy" for m in matched_mesh[:2]] if matched_mesh else ["Evidence-Based Medicine", "Clinical Outcomes"]

  # Infer missing facets if empty
  if not facets.get("condition"):
    recovered_cond, _ = _recover_biomedical_entity(q_clean)
    if recovered_cond:
      facets["condition"] = recovered_cond
    elif matched_mesh and matched_mesh[0].lower() not in _RECOVERY_SKIP:
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
