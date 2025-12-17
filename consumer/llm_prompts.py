"""
LLM Prompt Templates for Clinical Triage.

Contains the system prompt and formatting logic for generating
structured clinical summaries from vital signs data.
"""

# Clinical Triage System Prompt
CLINICAL_TRIAGE_SYSTEM_PROMPT = """You are an expert Clinical Triage Specialist working in a Remote Patient Monitoring (RPM) center. Your task is to analyze a single, newly arrived critical vital signs reading for a patient and immediately generate a structured clinical triage report.

**Your Protocol:**
1. **Analyze the Data:** Review the current vital signs and the timestamp. The patient's vital signs have already triggered a 'Critical' flag by an edge-classifier.
2. **Determine Severity:** Based *only* on the input data, perform a deeper clinical classification and assign a `risk_score` (0.0 to 1.0).
3. **Chain-of-Thought (CoT) Reasoning:** Write a detailed, step-by-step internal reasoning process in the `clinical_reasoning_cot` field. This must include:
    a. Identification of all abnormal vital signs (using standard clinical thresholds, e.g., HR < 50 or > 120, SpO2 < 90%).
    b. The pathological significance of these abnormalities (e.g., "HR 160 bpm indicates severe tachycardia, which risks myocardial ischemia").
    c. Justification for the chosen `triage_level` and `chief_concern`.
4. **Actionable Recommendations:** Provide a list of 3-5 specific, high-priority clinical actions.

**Constraint:** You **must** output a single, valid JSON object that strictly adheres to the provided schema. Do not output any other text, pre-amble, or explanation outside of the JSON structure."""


def format_vital_signs_for_llm(patient_id: str, timestamp: str, vitals: dict) -> str:
    """
    Format vital signs data as input for the LLM.
    
    Args:
        patient_id: The patient identifier.
        timestamp: ISO format timestamp of the reading.
        vitals: Dictionary containing heart_rate, spo2, temperature.
        
    Returns:
        Formatted string for LLM input.
    """
    return f"""---
Patient ID: {patient_id}
Reading Time (UTC): {timestamp}
Vital Signs:
  - Heart Rate (HR): {vitals['heart_rate']} bpm
  - Oxygen Saturation (SpO₂): {vitals['spo2']}%
  - Temperature (Temp): {vitals['temperature']}°C
---"""


def get_schema_for_llm() -> dict:
    """
    Get the JSON schema that the LLM must follow.
    
    Returns:
        JSON schema dictionary for ClinicianTriageSchema.
    """
    from consumer.schemas import ClinicianTriageSchema
    return ClinicianTriageSchema.model_json_schema()


def build_llm_prompt(patient_id: str, timestamp: str, vitals: dict) -> dict:
    """
    Build the complete prompt for the LLM API call.
    
    Args:
        patient_id: The patient identifier.
        timestamp: ISO format timestamp of the reading.
        vitals: Dictionary containing vital signs.
        
    Returns:
        Dictionary with 'system' and 'user' messages, plus 'schema'.
    """
    return {
        'system': CLINICAL_TRIAGE_SYSTEM_PROMPT,
        'user': format_vital_signs_for_llm(patient_id, timestamp, vitals),
        'schema': get_schema_for_llm()
    }
