from __future__ import annotations

from typing import Any

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

# Updated entity types for clinical trials
PROMPTS["DEFAULT_ENTITY_TYPES"] = [
    "trial",
    "condition",
    "intervention",
    "inclusion_eligibility_criteria",
    "exclusion_eligibility_criteria",
]

PROMPTS["DEFAULT_USER_PROMPT"] = "n/a"


PROMPTS["entity_extraction"] = """---Goal---
Given a clinical trial document (or a fragment of it) and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

---Steps---
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity and capitalize the name
- entity_type: One of the following types: [{entity_types}]
- entity_description: Provide a comprehensive description of the entity's attributes and activities *based solely on the information present in the input text*. **Do not infer or hallucinate information not explicitly stated.** If the text provides insufficient information to create a comprehensive description, state "Description not available in text."
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Entity_types: [{entity_types}]
Text:
{input_text}
######################
Output:"""
# PROMPTS["entity_extraction"] = """---Goal---
# Given a clinical trial document (or a fragment of it), build a structured knowledge graph centered on the provided clinical trial ID.
# The graph must include all relevant entities and relationships that are important for clinical trial matching and analysis.

# ---Inputs---
# - trial_id: {trial_id}   # ALWAYS use this exact value as the central node ID
# - section_name (optional): {section_name}
# - entity_types: [{entity_types}]
# - tuple_delimiter: {tuple_delimiter}
# - record_delimiter: {record_delimiter}
# - completion_delimiter: {completion_delimiter}

# ---Global Constraints---
# - The clinical trial with ID = {trial_id} MUST be represented as the **central node** (entity_type = "trial").
# - Every non-trial entity must be connected directly or indirectly to {trial_id}.
# - Use ONLY facts stated or strongly implied by the text. Do **not** hallucinate.
# - Keep names and spellings consistent across entities and relationships.
# - For relationship_strength, use a numeric score in [0.0, 1.0] with two decimals (e.g., 0.85).

# ---Section Guidance (if section_name provided)---
# - Treat {section_name} as a context hint about which part of the trial the text comes from.
# - If section_name describes eligibility (e.g., "INCLUSION CRITERIA", "EXCLUSION CRITERIA"), then:
#   * Prefer entity_type "eligibility" where appropriate.
#   * Use relationship_keywords like "eligible_if" or "excluded_if".
#   * Reflect the section in relationship_description (e.g., “per INCLUSION CRITERIA: …”).
# - If section_name refers to other parts (e.g., "INTERVENTION", "OUTCOMES", "LOCATIONS"), prefer relationship_keywords accordingly (e.g., "treats", "measures", "conducted_at", "located_in", "sponsored_by", "collaborates_with").
# - If section_name is empty, proceed normally.

# ---Steps---

# 1) Define the central trial entity:
#    - Create exactly one entity for the trial with:
#      * entity_name = {trial_id}
#      * entity_type = "trial"
#      * entity_description = concise but comprehensive summary of trial attributes present in the text (title, phase, status, design, arms, etc. when available).

#    Format:
#    ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

# 2) Identify all other entities. For each entity, extract:
#    - entity_name: Name in the same language as input. Capitalize proper names in English.
#    - entity_type: One of [{entity_types}]
#      * trial: The clinical trial itself (already created for {trial_id})
#      * condition: Disease/indication being studied
#      * intervention: Drug/device/biologic/procedure being tested
#      * sponsor: Lead sponsor, collaborator, or funding organization
#      * site: Facility/site where the trial is conducted
#      * geo: Geographic location (city, state, country, region)
#      * eligibility: Patient selection criteria (inclusion/exclusion, age, diagnosis requirements)
#    - entity_description: Concise but comprehensive description of the entity’s attributes and role in the trial.
#      If section_name is provided, reference it when helpful (e.g., “Eligibility factor from INCLUSION CRITERIA: …”).

#    Format for each:
#    ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

# 3) Extract relationships:
#    - Every non-trial entity should have at least one relationship to {trial_id}.
#    - Also capture meaningful relationships between non-trial entities (e.g., sponsor ↔ site, condition ↔ intervention).
#    - For each relationship, extract:
#      * source_entity
#      * target_entity
#      * relationship_description: short explanation grounded in the text; if section_name is provided, reference it when relevant (e.g., “per EXCLUSION CRITERIA: …”).
#      * relationship_keywords: pick 1–3 from this controlled list when applicable:
#        ["treats","investigates","eligible_if","excluded_if","contraindicated_with","requires","measures","outcome_of",
#         "located_in","conducted_at","sponsored_by","collaborates_with","funded_by","has_phase","has_status","targets"]
#        If none fit, use a precise custom verb-noun phrase (snake_case).
#      * relationship_strength: float in [0.00, 1.00] with two decimals indicating confidence/strength.

#    Format for each:
#    ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

#    Notes:
#    - Use exact entity_name strings used in the entity tuples.
#    - Prefer direct links to {trial_id} for primary relations (e.g., intervention→trial, condition→trial, site→trial, sponsor→trial).
#    - When eligibility constraints apply to a condition/intervention, link eligibility→trial and also eligibility→condition/intervention where appropriate.

# 4) Identify high-level trial concepts (topics/themes) that summarize the trial.
#    - Provide 3–10 concise keywords/phrases (comma-separated).
#    - Include section-aware terms when section_name is present (e.g., “inclusion criteria”, “exclusion criteria”, “dose escalation”, “primary endpoint”).

#    Format:
#    ("content_keywords"{tuple_delimiter}<high_level_keywords>)

# 5) Output formatting rules:
#    - Return ALL entities and relationships (and the content_keywords line) as a single flat list, joining items with {record_delimiter}.
#    - Do NOT include any extra text outside of the tuples.
#    - ALWAYS end with {completion_delimiter} on its own.

# ######################
# ---Examples---
# ######################
# {examples}

# #############################
# ---Real Data---
# ######################
# Entity_types: [{entity_types}]
# trial_id: {trial_id}
# section_name: {section_name}
# Text:
# {input_text}
# ######################
# Output:
# """
# PROMPTS["entity_extraction"] = """---Goal---
# From a full clinical trial document and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

# ---Global Constraints---
# - Emit a central "trial" entity with entity_name = {trial_id}.
# - Keep names/spellings consistent across entities and relations.
# - Connectivity requirement: Every non-trial entity you output MUST have at least one evidence-backed path to {trial_id} (direct or via other entities) using relations present in this document.
#   - If you cannot justify any path from an entity to {trial_id} based on this document, omit that entity.
#   - Canonicalization & reuse: Deduplicate entities within this output. Use the exact same entity_name strings in all relationships.
# - relationship_strength in [0.00, 1.00], two decimals.

# ---Eligibility Guidance---
# - Model atomic eligibility criteria as separate entities (entity_type="inclusion_eligibility_criteria" or "exclusion_eligibility_criteria")

# ---Steps---

# 1. Central trial entity (always emit):
# ("entity"{tuple_delimiter}{trial_id}{tuple_delimiter}"trial"{tuple_delimiter}<concise trial summary">)

# 2. Other entities (repeat):
# ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<concise description based on document>)

# 3. Relationships (repeat):
# - Capture any meaningful links: trial↔non-trial and non-trial↔non-trial.
# - Fields:
#   * source_entity: name of the source entity, as identified in step 1
#   * target_entity: name of the target entity, as identified in step 1
#   * relationship_description: explanation as to why you think the source entity and the target entity are related to each other
#   * relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
#   * relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity, in [0.00, 1.00]

# Format:
# ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

# 4. Content keywords (3–10 concise terms capturing trial themes:
# ("content_keywords"{tuple_delimiter}<keywords_comma_separated>)

# 5. Return output in a singlelist of all the entities and relationships identified in steps 1, 2 and 3. Use **{record_delimiter}** as the list delimiter.

# 6. When finished, output {completion_delimiter}

# ######################
# ---Examples---
# ######################
# {examples}

# #############################
# ---Real Data---
# ######################
# Entity_types: [{entity_types}]
# trial_id: {trial_id}
# Text:
# {input_text}
# ######################
# Output:
# """


PROMPTS["entity_extraction_examples"] = [
    """Example:

Entity_types: [trial, condition, intervention, inclusion_eligibility_criteria, exclusion_eligibility_criteria]
Text:
```
NCT02345798: A Phase 3 Study of Pembrolizumab (MK-3475) in Participants With Advanced Non-Small Cell Lung Cancer

Brief Title: A Phase 3 Study of Pembrolizumab (MK-3475) in Participants With Advanced Non-Small Cell Lung Cancer
Official Title: A Phase 3, Randomized, Double-Blind Study of Pembrolizumab (MK-3475) Versus Placebo in Participants With Previously Treated Advanced Non-Small Cell Lung Cancer

Status: Completed
Phase: Phase 3
Study Type: Interventional
Enrollment: 1034 participants

Conditions: Non-Small Cell Lung Cancer, Advanced Cancer
Interventions: Pembrolizumab 200 mg IV every 3 weeks, Placebo IV every 3 weeks
Keywords: Immunotherapy, PD-1 inhibitor, Checkpoint inhibitor

Brief Summary: This study evaluates the efficacy and safety of pembrolizumab compared to placebo in participants with previously treated advanced non-small cell lung cancer. Participants will be randomized to receive either pembrolizumab or placebo.

Eligibility Criteria: 
- Age 18 years or older
- Histologically confirmed advanced NSCLC
- Previously treated with platinum-based chemotherapy
- ECOG performance status 0 or 1

Primary Outcome Measures:
- Overall Survival (OS)
- Progression-Free Survival (PFS)

Sponsor: Merck Sharp & Dohme LLC
Lead Sponsor: Merck Sharp & Dohme LLC
Study Sites: Multiple sites across United States and Europe
```

Output:
("entity"{tuple_delimiter}"NCT02345798"{tuple_delimiter}"trial"{tuple_delimiter}"Phase 3 randomized double-blind study evaluating pembrolizumab versus placebo in 1034 participants with previously treated advanced NSCLC."){record_delimiter}
("entity"{tuple_delimiter}"Non-Small Cell Lung Cancer"{tuple_delimiter}"condition"{tuple_delimiter}"Advanced form of lung cancer that is the primary disease/indication studied."){record_delimiter}
("entity"{tuple_delimiter}"Advanced Cancer"{tuple_delimiter}"condition"{tuple_delimiter}"General category of advanced malignancy including NSCLC."){record_delimiter}
("entity"{tuple_delimiter}"Pembrolizumab"{tuple_delimiter}"intervention"{tuple_delimiter}"Anti-PD-1 immunotherapy administered 200mg IV every 3 weeks."){record_delimiter}
("entity"{tuple_delimiter}"Placebo"{tuple_delimiter}"intervention"{tuple_delimiter}"Control IV infusion every 3 weeks."){record_delimiter}
("entity"{tuple_delimiter}"Age ≥ 18 years"{tuple_delimiter}"inclusion_eligibility_criteria"{tuple_delimiter}"INCLUSION: Adults aged 18 years or older."){record_delimiter}
("entity"{tuple_delimiter}"Histologically confirmed advanced NSCLC"{tuple_delimiter}"inclusion_eligibility_criteria"{tuple_delimiter}"INCLUSION: Diagnosis required for study entry."){record_delimiter}
("entity"{tuple_delimiter}"Prior platinum-based chemotherapy"{tuple_delimiter}"inclusion_eligibility_criteria"{tuple_delimiter}"INCLUSION: Must have been previously treated with platinum-based chemotherapy."){record_delimiter}
("entity"{tuple_delimiter}"ECOG performance status 0–1"{tuple_delimiter}"inclusion_eligibility_criteria"{tuple_delimiter}"INCLUSION: Functional status requirement."){record_delimiter}

("relationship"{tuple_delimiter}"NCT02345798"{tuple_delimiter}"Non-Small Cell Lung Cancer"{tuple_delimiter}"Trial investigates pembrolizumab in advanced NSCLC."{tuple_delimiter}"disease_focus"{tuple_delimiter}0.95){record_delimiter}
("relationship"{tuple_delimiter}"Pembrolizumab"{tuple_delimiter}"Non-Small Cell Lung Cancer"{tuple_delimiter}"Pembrolizumab tested as treatment for NSCLC."{tuple_delimiter}"treats"{tuple_delimiter}0.94){record_delimiter}
("relationship"{tuple_delimiter}"Pembrolizumab"{tuple_delimiter}"NCT02345798"{tuple_delimiter}"Experimental arm of the trial."{tuple_delimiter}"investigates"{tuple_delimiter}0.92){record_delimiter}
("relationship"{tuple_delimiter}"Placebo"{tuple_delimiter}"NCT02345798"{tuple_delimiter}"Comparator control arm."{tuple_delimiter}"control_arm"{tuple_delimiter}0.90){record_delimiter}
("relationship"{tuple_delimiter}"Age ≥ 18 years"{tuple_delimiter}"NCT02345798"{tuple_delimiter}"INCLUSION: Minimum age requirement."{tuple_delimiter}"eligible_inclusion"{tuple_delimiter}0.90){record_delimiter}
("relationship"{tuple_delimiter}"Histologically confirmed advanced NSCLC"{tuple_delimiter}"Non-Small Cell Lung Cancer"{tuple_delimiter}"INCLUSION: Diagnosis required."{tuple_delimiter}"eligible_inclusion"{tuple_delimiter}0.92){record_delimiter}
("relationship"{tuple_delimiter}"Prior platinum-based chemotherapy"{tuple_delimiter}"Pembrolizumab"{tuple_delimiter}"INCLUSION: Patients must have prior platinum therapy before receiving pembrolizumab."{tuple_delimiter}"eligible_inclusion, requires"{tuple_delimiter}0.88){record_delimiter}
("relationship"{tuple_delimiter}"ECOG performance status 0–1"{tuple_delimiter}"NCT02345798"{tuple_delimiter}"INCLUSION: Functional status eligibility."{tuple_delimiter}"eligible_inclusion"{tuple_delimiter}0.90){record_delimiter}
#############################"""
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of clinical trial data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we have full context.
Use {language} as output language.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS["entity_continue_extraction"] = """
MANY entities and relationships were missed in the last extraction. Please find only the missing entities and relationships from previous text.

---Remember Steps---

1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name
- entity_type: One of the following types: [{entity_types}]
- entity_description: Provide a comprehensive description of the entity's attributes and activities *based solely on the information present in the input text*. **Do not infer or hallucinate information not explicitly stated.** If the text provides insufficient information to create a comprehensive description, state "Description not available in text."
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

---Output---

Add new entities and relations below using the same format, and do not include entities and relations that have been previously extracted. :\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---'

It appears some entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["fail_response"] = (
    "Sorry, I'm not able to provide an answer to that question.[no-context]"
)

# PROMPTS["rag_response"] = """---Role---

# You are a helpful assistant responding to user query about Knowledge Graph and Document Chunks provided in JSON format below.


# ---Goal---

# Generate a concise response based on Knowledge Base and follow Response Rules, considering both current query and the conversation history if provided. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. Do not include information not provided by Knowledge Base.

# ---Conversation History---
# {history}

# ---Knowledge Graph and Document Chunks---
# {context_data}

# ---RESPONSE GUIDELINES---
# **1. Content & Adherence:**
# - Strictly adhere to the provided context from the Knowledge Base. Do not invent, assume, or include any information not present in the source data.
# - If the answer cannot be found in the provided context, state that you do not have enough information to answer.
# - Ensure the response maintains continuity with the conversation history.

# **2. Formatting & Language:**
# - Format the response using markdown with appropriate section headings.
# - The response language must in the same language as the user's question.
# - Target format and length: {response_type}

# **3. Citations / References:**
# - At the end of the response, under a "References" section, each citation must clearly indicate its origin (KG or DC).
# - The maximum number of citations is 5, including both KG and DC.
# - Use the following formats for citations:
#   - For a Knowledge Graph Entity: `[KG] <entity_name>`
#   - For a Knowledge Graph Relationship: `[KG] <entity1_name> - <entity2_name>`
#   - For a Document Chunk: `[DC] <file_path_or_document_name>`

# ---USER CONTEXT---
# - Additional user prompt: {user_prompt}


# Response:"""
PROMPTS["rag_response"] = """---Role---
You are a matching engine that, given a patient profile and a Knowledge Base (clinical-trial Knowledge Graph + document chunks), returns the best-matching clinical trial IDs.

---Goal---
From the provided Knowledge Base, identify clinical trials for which the patient likely qualifies and output only the list of clinical trial IDs, ranked by match quality. Do not use any information outside the provided Knowledge Base.

---Inputs---
- Patient Profile:
{user_prompt}

- Knowledge Graph and Document Chunks:
{context_data}

---RESPONSE RULES---
1) Content & Adherence
- Use only data present in the Knowledge Base (KG/DC). Do not invent or assume missing details.
- If eligibility/status/location information is absent for a trial, do not assume it; match using what is available.
- Prefer trials whose inclusion criteria are satisfied and whose exclusion criteria are not violated by the patient profile.
- When available, favor trials that are Recruiting/Active and within plausible geographic reach; if status/location is not provided, do not filter on it.

2) Matching Logic (internal guidance; do not output explanations)
- Extract key patient attributes: condition/diagnosis, stage/severity, biomarkers/genetics, prior therapies, age/sex, comorbidities, ECOG, lab values, geography, and other relevant fields present.
- For each trial, compare inclusion and exclusion criteria against the patient attributes.
- Compute a match quality signal (e.g., count of satisfied inclusions, absence of exclusions, closeness on age/ECOG, etc.) using only provided data.
- Rank trials by match quality; break ties by stricter inclusion matches, then more recent/active status when available, then lexicographically by trial ID.

3) Output Format & Language
- Output MUST be only a JSON array of **unique clinical trial IDs** (strings), e.g. ["NCT01234567","NCT08976543"].
- Return **all** trials from the Knowledge Base that you judge suitable based on the rules above (any number is allowed, but should be larger than 10).
- If no suitable trials are found from the provided Knowledge Base, output [].
- No additional text, no explanations, no citations, no code fences.

Response:"""


PROMPTS["keywords_extraction"] = """---Role---
You are an expert keyword extractor, specializing in analyzing user queries for a Retrieval-Augmented Generation (RAG) system. Your purpose is to identify both high-level and low-level keywords in the user's query that will be used for effective document retrieval.

---Goal---
Given a user query, your task is to extract two distinct types of keywords:
1. **high_level_keywords**: for overarching concepts or themes, capturing user's core intent, the subject area, or the type of question being asked.
2. **low_level_keywords**: for specific entities or details, identifying the specific entities, proper nouns, technical jargon, product names, or concrete items.

---Instructions & Constraints---
1. **Output Format**: Your output MUST be a valid JSON object and nothing else. Do not include any explanatory text, markdown code fences (like ```json), or any other text before or after the JSON. It will be parsed directly by a JSON parser.
2. **Source of Truth**: All keywords must be explicitly derived from the user query, with both high-level and low-level keyword categories required to contain content.
3. **Concise & Meaningful**: Keywords should be concise words or meaningful phrases. Prioritize multi-word phrases when they represent a single concept. For example, from "latest financial report of Apple Inc.", you should extract "latest financial report" and "Apple Inc." rather than "latest", "financial", "report", and "Apple".
4. **Handle Edge Cases**: For queries that are too simple, vague, or nonsensical (e.g., "hello", "ok", "asdfghjkl"), you must return a JSON object with empty lists for both keyword types.

---Examples---
{examples}

---Real Data---
User Query: {query}

---Output---
"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does international trade influence global economic stability?"

Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}

""",
    """Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"

Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}

""",
    """Example 3:

Query: "What is the role of education in reducing poverty?"

Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}

""",
]

PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Document Chunks provided provided in JSON format below.

---Goal---

Generate a concise response based on Document Chunks and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Document Chunks, and incorporating general knowledge relevant to the Document Chunks. Do not include information not provided by Document Chunks.

---Conversation History---
{history}

---Document Chunks(DC)---
{content_data}

---RESPONSE GUIDELINES---
**1. Content & Adherence:**
- Strictly adhere to the provided context from the Knowledge Base. Do not invent, assume, or include any information not present in the source data.
- If the answer cannot be found in the provided context, state that you do not have enough information to answer.
- Ensure the response maintains continuity with the conversation history.

**2. Formatting & Language:**
- Format the response using markdown with appropriate section headings.
- The response language must match the user's question language.
- Target format and length: {response_type}

**3. Citations / References:**
- At the end of the response, under a "References" section, cite a maximum of 5 most relevant sources used.
- Use the following formats for citations: `[DC] <file_path_or_document_name>`

---USER CONTEXT---
- Additional user prompt: {user_prompt}


Response:"""
