
import json
import os
import sys
import time
import logging
from consumer.app import create_app, message_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_static_data():
    """
    Reads validation_data.json and processes records via the existing message handler.
    """
    json_path = os.path.join(os.path.dirname(__file__), 'validation_data.json')
    logger.info(f"📂 Loading static validation data from: {json_path}")

    if not os.path.exists(json_path):
        logger.error("❌ Validation file not found!")
        return

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load JSON: {e}")
        return

    logger.info(f"🔎 Found {len(data)} records. Starting processing...")
    
    # Initialize Flask App context
    app = create_app()
    handler = message_handler(app)

    # Dummy commit function (always succeeds)
    def dummy_commit():
        return True

    success_count = 0
    fail_count = 0

    for i, record in enumerate(data):
        logger.info(f"Processing Record {i+1}/{len(data)}: Patient {record['patient_id']}")

        # TRANSFORM: Flat JSON -> Nested Structure expected by app.py
        # Logic to match Producer's structure
        
        # Simple classification based on thresholds
        hr = record.get('heart_rate', 0)
        spo2 = record.get('spo2', 100)
        state = 'Normal'
        if hr < 50 or hr > 130 or spo2 < 90:
            state = 'Critical'
            logger.warning(f"⚠️ Classified as CRITICAL: HR={hr}, SpO2={spo2}")

        nested_data = {
            'patient_id': record['patient_id'],
            'timestamp': record['timestamp'],
            'device_id': 'static-validation-file',
            'vitals': {
                'heart_rate': hr,
                'spo2': spo2,
                'temperature': record.get('body_temp', 37.0)
            },
            'state_classified': state
        }

        # Process
        try:
            # We pass a dummy callback for commit_fn
            processed = handler(
                data=nested_data, 
                partition=0, 
                offset=i, 
                commit_fn=dummy_commit
            )
            
            if processed:
                success_count += 1
                logger.info(f"✅ Record {i+1} processed successfully")
            else:
                fail_count += 1
                logger.error(f"❌ Record {i+1} failed processing")
                
        except Exception as e:
            logger.error(f"💥 Exception processing record {i+1}: {e}")
            fail_count += 1

    logger.info("-" * 40)
    logger.info("🏁 Static Validation Complete")
    logger.info(f"Summary: {success_count} Succeeded, {fail_count} Failed")
    logger.info("Keeping container alive for inspection... (Ctrl+C to exit)")
    
    # Keep alive so we can inspect logs without container restarting loop
    while True:
        time.sleep(10)

if __name__ == "__main__":
    process_static_data()
