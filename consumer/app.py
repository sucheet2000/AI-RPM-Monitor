"""
Flask Consumer Service for AI-RPM-Monitor.

Acts as a Kafka consumer, persisting vitals to PostgreSQL and
exposing REST API endpoints for querying patient data.
"""
import os
import json
import threading
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from consumer.models import db, VitalsRecord, LLMSummary
from consumer.models import db, VitalsRecord, LLMSummary
from consumer.kafka_consumer import VitalsConsumer
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory for the consumer service.
    
    Args:
        config_name: Optional configuration name.
        
    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'consumer-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://rpm_user:rpm_password@localhost:5432/rpm_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Kafka configuration
    app.config['KAFKA_BOOTSTRAP_SERVERS'] = os.environ.get(
        'KAFKA_BOOTSTRAP_SERVERS',
        'localhost:9093'
    )
    app.config['KAFKA_VITALS_TOPIC'] = os.environ.get(
        'KAFKA_VITALS_TOPIC',
        'vitals'
    )
    
    # Initialize extensions
    db.init_app(app)
    
    # Register API routes
    register_routes(app)
    
    return app


def register_routes(app: Flask) -> None:
    """Register API routes on the Flask app."""
    
    @app.route('/')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'AI-RPM-Monitor Consumer',
            'version': '0.1.0'
        })
    
    @app.route('/api/vitals/<patient_id>', methods=['GET'])
    def get_patient_vitals(patient_id: str):
        """
        Get vital records for a patient from the last 24 hours.
        
        Args:
            patient_id: The patient identifier.
            
        Query Parameters:
            hours: Optional, number of hours to look back (default: 24).
            limit: Optional, maximum records to return (default: 100).
            
        Returns:
            JSON array of vital records.
        """
        try:
            # Parse query parameters
            hours = request.args.get('hours', 24, type=int)
            limit = request.args.get('limit', 100, type=int)
            
            # Validate parameters
            hours = max(1, min(hours, 168))  # 1 hour to 7 days
            limit = max(1, min(limit, 1000))
            
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            # Query database
            records = VitalsRecord.query.filter(
                VitalsRecord.patient_id == patient_id,
                VitalsRecord.reading_timestamp >= time_threshold
            ).order_by(
                VitalsRecord.reading_timestamp.desc()
            ).limit(limit).all()
            
            return jsonify({
                'patient_id': patient_id,
                'period_hours': hours,
                'count': len(records),
                'records': [record.to_dict() for record in records]
            })
            
        except Exception as e:
            logger.error(f"Error fetching vitals for {patient_id}: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    
    @app.route('/api/alerts/<patient_id>', methods=['GET'])
    def get_patient_alerts(patient_id: str):
        """
        Get all Critical alerts for a patient.
        
        Args:
            patient_id: The patient identifier.
            
        Query Parameters:
            limit: Optional, maximum records to return (default: 50).
            since: Optional, ISO timestamp to filter from.
            
        Returns:
            JSON array of critical vital records.
        """
        try:
            # Parse query parameters
            limit = request.args.get('limit', 50, type=int)
            since = request.args.get('since', None, type=str)
            
            # Validate limit
            limit = max(1, min(limit, 500))
            
            # Build query
            query = VitalsRecord.query.filter(
                VitalsRecord.patient_id == patient_id,
                VitalsRecord.state_classified == 'Critical'
            )
            
            # Apply since filter if provided
            if since:
                try:
                    since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                    query = query.filter(VitalsRecord.reading_timestamp >= since_dt)
                except ValueError:
                    return jsonify({
                        'error': 'Invalid timestamp format',
                        'message': 'Use ISO 8601 format (e.g., 2024-01-01T00:00:00Z)'
                    }), 400
            
            # Execute query
            records = query.order_by(
                VitalsRecord.reading_timestamp.desc()
            ).limit(limit).all()
            
            return jsonify({
                'patient_id': patient_id,
                'alert_type': 'Critical',
                'count': len(records),
                'alerts': [record.to_dict() for record in records]
            })
            
        except Exception as e:
            logger.error(f"Error fetching alerts for {patient_id}: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    
    @app.route('/api/summaries/<patient_id>', methods=['GET'])
    def get_patient_summaries(patient_id: str):
        """
        Get LLM-generated summaries for a patient.
        
        Args:
            patient_id: The patient identifier.
            
        Returns:
            JSON array of LLM summaries.
        """
        try:
            limit = request.args.get('limit', 10, type=int)
            limit = max(1, min(limit, 50))
            
            summaries = LLMSummary.query.filter(
                LLMSummary.patient_id == patient_id
            ).order_by(
                LLMSummary.created_at.desc()
            ).limit(limit).all()
            
            return jsonify({
                'patient_id': patient_id,
                'count': len(summaries),
                'summaries': [s.to_dict() for s in summaries]
            })
            
        except Exception as e:
            logger.error(f"Error fetching summaries for {patient_id}: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get overall system statistics."""
        try:
            total_records = VitalsRecord.query.count()
            critical_count = VitalsRecord.query.filter(
                VitalsRecord.state_classified == 'Critical'
            ).count()
            warning_count = VitalsRecord.query.filter(
                VitalsRecord.state_classified == 'Warning'
            ).count()
            
            # Get unique patient count
            patient_count = db.session.query(
                VitalsRecord.patient_id
            ).distinct().count()
            
            return jsonify({
                'total_records': total_records,
                'patient_count': patient_count,
                'by_state': {
                    'Critical': critical_count,
                    'Warning': warning_count,
                    'Normal': total_records - critical_count - warning_count
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500


def message_handler(app: Flask):
    """
    Create a message handler that persists to database with At-Least-Once semantics.
    
    The handler writes the vital record and LLM summary (for critical readings)
    to the database, then commits the Kafka offset only after both writes succeed.
    
    Args:
        app: Flask application with database context.
        
    Returns:
        Handler function for Kafka messages.
    """
    def handler(data: dict, partition: int, offset: int, commit_fn) -> bool:
        """
        Persist a consumed message to the database and commit offset.
        
        Args:
            data: Decoded message dictionary.
            partition: Kafka partition number.
            offset: Kafka message offset.
            commit_fn: Callback to commit offset after successful processing.
            
        Returns:
            True if processing and commit succeeded, False otherwise.
        """
        with app.app_context():
            try:
                # Parse timestamp
                reading_ts = datetime.fromisoformat(
                    data['timestamp'].replace('Z', '+00:00')
                )
                
                # --- STEP 1: Create and persist VitalsRecord ---
                record = VitalsRecord(
                    patient_id=data['patient_id'],
                    device_id=data.get('device_id'),
                    heart_rate=data['vitals']['heart_rate'],
                    spo2=data['vitals']['spo2'],
                    temperature=data['vitals']['temperature'],
                    state_classified=data['state_classified'],
                    reading_timestamp=reading_ts,
                    kafka_partition=partition,
                    kafka_offset=offset
                )
                
                db.session.add(record)
                
                # --- STEP 2: Generate LLM Summary for Critical readings ---
                llm_summary = None
                if data['state_classified'] == 'Critical':
                    llm_summary = generate_critical_summary(data, reading_ts)
                    db.session.add(llm_summary)
                    
                    logger.warning(
                        f"🔴 CRITICAL ALERT: Patient {data['patient_id']} - "
                        f"HR={data['vitals']['heart_rate']}, "
                        f"SpO2={data['vitals']['spo2']}, "
                        f"Temp={data['vitals']['temperature']}"
                    )
                
                # --- STEP 3: Commit database transaction ---
                db.session.commit()
                logger.debug(
                    f"✓ Persisted vital record for {data['patient_id']} "
                    f"[partition={partition}, offset={offset}]"
                )
                
                # --- STEP 4: Commit Kafka offset ONLY after DB success ---
                if not commit_fn():
                    logger.error(
                        f"DB write succeeded but Kafka commit failed for "
                        f"partition {partition}, offset {offset}"
                    )
                    # Still return True since data was persisted
                    # (may result in duplicate on restart, but that's At-Least-Once)
                
                return True
                    
            except Exception as e:
                logger.error(f"Failed to persist message: {e}")
                db.session.rollback()
                # Return False - don't commit offset, message will be reprocessed
                return False
    
    return handler


def generate_critical_summary(data: dict, reading_ts: datetime) -> LLMSummary:
    """
    Generates a structured LLM summary for a critical vital reading using the Gemini API 
    and Pydantic to enforce the ClinicianTriageSchema.
    
    Args:
        data: The vital signs data dictionary.
        reading_ts: The reading timestamp.
        
    Returns:
        LLMSummary model instance with structured JSON output.
    """
    from google import genai
    from pydantic import ValidationError
    from consumer.schemas import ClinicianTriageSchema
    
    vitals = data['vitals']
    patient_id = data['patient_id']
    
    # 1. Setup - Initialize Gemini Client
    try:
        client = genai.Client()
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}")
        # Return a fallback summary to avoid blocking processing
        return LLMSummary(
            patient_id=patient_id,
            summary_text="FATAL ERROR: LLM Triage failed to initialize client.",
            recommendation="Urgent manual clinical review required. Check API key.",
            risk_score=1.0,
            triage_level='Immediate',
            period_start=reading_ts,
            period_end=reading_ts,
            model_version='LLM_INIT_ERROR'
        )
    
    model_name = 'gemini-2.5-flash'  # Fast model for real-time processing
    
    # System Instruction (Clinical Triage Protocol)
    SYSTEM_INSTRUCTION = (
        "You are an expert Clinical Triage Specialist working in a Remote Patient Monitoring (RPM) center. "
        "Your task is to analyze a single, newly arrived critical vital signs reading for a patient and "
        "immediately generate a structured clinical triage report.\n\n"
        "**Your Protocol:**\n"
        "1. **Analyze the Data:** Review the current vital signs and the timestamp. The patient's vital signs "
        "have already triggered a 'Critical' flag by an edge-classifier.\n"
        "2. **Determine Severity:** Based *only* on the input data, perform a deeper clinical classification "
        "and assign a `risk_score` (0.0 to 1.0).\n"
        "3. **Chain-of-Thought (CoT) Reasoning:** Write a detailed, step-by-step internal reasoning process "
        "in the `clinical_reasoning_cot` field. This must include: a. Identification of all abnormal vital signs. "
        "b. The pathological significance of these abnormalities. c. Justification for the chosen `triage_level` "
        "and `chief_concern`.\n"
        "4. **Actionable Recommendations:** Provide a list of 3-5 specific, high-priority clinical actions.\n\n"
        "**Constraint:** You **must** output a single, valid JSON object that strictly adheres to the provided schema. "
        "Do not output any other text, pre-amble, or explanation outside of the JSON structure."
    )
    
    # User Prompt (dynamic context)
    user_prompt = (
        f"Analyze the following critical vital signs. Generate the structured triage report.\n\n"
        f"--- Input Data ---\n"
        f"Patient ID: {patient_id}\n"
        f"Reading Time (UTC): {reading_ts.isoformat()}Z\n"
        f"Vital Signs:\n"
        f"  - Heart Rate (HR): {vitals['heart_rate']} bpm\n"
        f"  - Oxygen Saturation (SpO₂): {vitals['spo2']}%\n"
        f"  - Temperature (Temp): {vitals['temperature']}°C\n"
        f"------------------\n"
    )

    # 2. Call the Gemini API with structured output
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
                # Pass the Pydantic class to force structured JSON output
                "response_schema": ClinicianTriageSchema,
                "temperature": 0.2  # Low temperature for consistent clinical output
            }
        )
        
        # 3. Parse the structured output
        triage_data: ClinicianTriageSchema = response.parsed
        
        # 4. Map the structured data to the LLMSummary DB model
        summary_text = (
            f"**Triage Level: {triage_data.triage_level}** | "
            f"**Chief Concern: {triage_data.chief_concern}** "
            f"(Risk Score: {triage_data.risk_score:.2f})\n"
            f"Critical Factors: {', '.join(triage_data.critical_factors)}\n\n"
            f"**LLM Reasoning (Chain-of-Thought):**\n"
            f"{triage_data.clinical_reasoning_cot}\n"
        )
        
        recommendation_text = "\n".join([
            f"[{rec.priority}] {rec.action}" for rec in triage_data.recommendations
        ])
        
        logger.info(
            f"🤖 LLM Triage completed for {patient_id}: "
            f"Level={triage_data.triage_level}, Risk={triage_data.risk_score:.2f}"
        )
        
        return LLMSummary(
            patient_id=patient_id,
            summary_text=summary_text,
            recommendation=recommendation_text,
            risk_score=triage_data.risk_score,
            triage_level=triage_data.triage_level,
            period_start=reading_ts,
            period_end=reading_ts,
            # Store the entire structured JSON for audit purposes
            structured_json=triage_data.model_dump(),
            model_version=model_name
        )
    
    except ValidationError as e:
        logger.error(f"LLM output validation failed for patient {patient_id}: {e}")
        # Fallback for structured output validation failure
        return LLMSummary(
            patient_id=patient_id,
            summary_text=f"ERROR: LLM Triage failed Pydantic validation. Exception: {str(e)}",
            recommendation="Urgent manual review required. Check LLM schema adherence.",
            risk_score=0.99,
            triage_level='Immediate',
            period_start=reading_ts,
            period_end=reading_ts,
            model_version='VALIDATION_ERROR'
        )
    except Exception as e:
        logger.error(f"LLM API call failed for patient {patient_id}: {e}")
        # Generic API/network failure fallback
        return LLMSummary(
            patient_id=patient_id,
            summary_text=f"ERROR: LLM Triage API call failed. Exception: {str(e)}",
            recommendation="Urgent manual review required. Check API connection/rate limits.",
            risk_score=0.99,
            triage_level='Immediate',
            period_start=reading_ts,
            period_end=reading_ts,
            model_version='LLM_API_ERROR'
        )


def run_consumer(app: Flask) -> None:
    """
    Run the Kafka consumer in a separate thread.
    
    Args:
        app: Flask application with database context.
    """
    consumer = VitalsConsumer(
        bootstrap_servers=app.config['KAFKA_BOOTSTRAP_SERVERS'],
        topic=app.config['KAFKA_VITALS_TOPIC']
    )
    
    handler = message_handler(app)
    
    # Run in a daemon thread
    consumer_thread = threading.Thread(
        target=consumer.consume,
        args=(handler,),
        daemon=True
    )
    consumer_thread.start()
    logger.info("Kafka consumer thread started")


# Application instance created only when run directly
if __name__ == '__main__':
    app = create_app()
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Start Kafka consumer in background
    run_consumer(app)
    
    # Run Flask server
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
