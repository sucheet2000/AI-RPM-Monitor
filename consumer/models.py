"""
Database models for the Kafka Consumer Service.

Defines VitalsRecord and LLMSummary tables for PostgreSQL persistence.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class VitalsRecord(db.Model):
    """
    Model for storing consumed vital signs records from Kafka.
    
    Each record represents a single vital reading for a patient,
    with classification state from the edge classifier.
    """
    __tablename__ = 'vitals_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False, index=True)
    device_id = db.Column(db.String(50))
    
    # Vital signs
    heart_rate = db.Column(db.Float, nullable=False)
    spo2 = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    
    # Classification
    state_classified = db.Column(db.String(20), nullable=False, index=True)
    
    # Timestamps
    reading_timestamp = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Kafka metadata
    kafka_partition = db.Column(db.Integer)
    kafka_offset = db.Column(db.BigInteger)
    
    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'device_id': self.device_id,
            'vitals': {
                'heart_rate': self.heart_rate,
                'spo2': self.spo2,
                'temperature': self.temperature
            },
            'state_classified': self.state_classified,
            'reading_timestamp': self.reading_timestamp.isoformat() + 'Z' if self.reading_timestamp else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
    
    def __repr__(self):
        return f'<VitalsRecord {self.id} - {self.patient_id} [{self.state_classified}]>'


class LLMSummary(db.Model):
    """
    Model for storing LLM-generated summaries of patient vitals.
    
    Contains AI-generated insights and recommendations based on
    aggregated vital readings. Includes structured_json field for
    validated ClinicianTriageSchema output.
    """
    __tablename__ = 'llm_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False, index=True)
    
    # Summary content (plain text)
    summary_text = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text)
    risk_score = db.Column(db.Float)
    
    # Structured LLM output (JSON)
    # Stores the validated ClinicianTriageSchema as JSON for automated processing
    structured_json = db.Column(db.JSON, nullable=True)
    
    # Triage level derived from structured output
    triage_level = db.Column(db.String(20), nullable=True, index=True)
    
    # Time range covered
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Metadata
    model_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'summary_text': self.summary_text,
            'recommendation': self.recommendation,
            'risk_score': self.risk_score,
            'triage_level': self.triage_level,
            'structured_json': self.structured_json,
            'period': {
                'start': self.period_start.isoformat() + 'Z' if self.period_start else None,
                'end': self.period_end.isoformat() + 'Z' if self.period_end else None
            },
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
    
    def __repr__(self):
        return f'<LLMSummary {self.id} - {self.patient_id}>'
