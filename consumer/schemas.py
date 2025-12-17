"""
Pydantic Schemas for Structured LLM Output.

Defines the exact JSON structure the LLM must return for automated clinical triage.
These schemas enable structured output parsing and validation.
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Annotated


# --- Pydantic Schema Definition ---

class TriageRecommendation(BaseModel):
    """Specific clinical actions recommended based on the patient's critical state."""
    action: str = Field(
        description="A specific, immediate clinical action (e.g., 'Administer Oxygen', 'Notify Attending Physician')."
    )
    priority: Literal['High', 'Medium', 'Low'] = Field(
        description="The urgency of the action."
    )


class ClinicianTriageSchema(BaseModel):
    """Structured clinical summary for a Critical vital reading, required for automated processing."""
    
    # Core Fields
    risk_score: Annotated[float, Field(ge=0.0, le=1.0, description=(
        "A calculated risk score between 0.0 (low) and 1.0 (highest) "
        "representing the patient's acute deterioration severity."
    ))]
    
    triage_level: Literal['Immediate', 'Urgent', 'Standard'] = Field(
        description=(
            "The recommended level of clinical response. "
            "'Immediate' is for life-threatening or rapidly deteriorating conditions."
        )
    )
    
    chief_concern: str = Field(
        description=(
            "The primary suspected medical issue (e.g., 'Severe Hypoxemia due to Respiratory Failure', "
            "'Malignant Hypertension')."
        )
    )
    
    critical_factors: List[str] = Field(
        description=(
            "A list of specific vital signs and their values driving the Critical classification "
            "(e.g., 'SpO2 85%', 'HR 160 bpm')."
        )
    )
    
    # Chain-of-Thought (CoT) Field
    clinical_reasoning_cot: str = Field(
        description=(
            "The detailed, step-by-step internal reasoning process used to arrive at the "
            "triage decision. This is crucial for audit and human validation."
        )
    )
    
    # Actionable Output
    recommendations: List[TriageRecommendation] = Field(
        description=(
            "A list of 3-5 specific, high-priority clinical recommendations "
            "to be immediately presented to the care team."
        )
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "risk_score": 0.85,
                "triage_level": "Immediate",
                "chief_concern": "Severe Hypoxemia with Bradycardia",
                "critical_factors": [
                    "SpO2 82% (Critical: <88%)",
                    "HR 38 bpm (Critical: <40 bpm)",
                    "Temp 34.5°C (Hypothermia)"
                ],
                "clinical_reasoning_cot": (
                    "Step 1: Observed SpO2 of 82%, which is significantly below the critical "
                    "threshold of 88%, indicating severe hypoxemia. Step 2: Heart rate of 38 bpm "
                    "indicates severe bradycardia, which combined with hypoxemia suggests "
                    "possible cardiogenic shock or respiratory arrest. Step 3: Body temperature "
                    "of 34.5°C indicates hypothermia, potentially exacerbating cardiac issues. "
                    "Step 4: The combination of these three critical factors warrants immediate "
                    "intervention as the patient is at high risk of cardiac arrest."
                ),
                "recommendations": [
                    {"action": "Initiate high-flow oxygen therapy immediately", "priority": "High"},
                    {"action": "Prepare for possible intubation", "priority": "High"},
                    {"action": "Notify attending physician and rapid response team", "priority": "High"},
                    {"action": "Establish IV access and prepare atropine for bradycardia", "priority": "Medium"},
                    {"action": "Initiate active rewarming protocol", "priority": "Medium"}
                ]
            }
        }
