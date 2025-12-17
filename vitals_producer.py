"""
Kafka Producer for Patient Vitals Data.

Generates synthetic patient vital signs (HR, SpO2, Temp), classifies them
using the edge classifier, and publishes to the Kafka 'vitals' topic.
"""
import json
import os
import time
import random
import uuid
from datetime import datetime
from typing import Optional
from confluent_kafka import Producer, KafkaError
from edge_classifier import EdgeClassifier, VitalReading, get_classifier


# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093'),
    'client.id': 'vitals-producer',
    'acks': 'all'
}

VITALS_TOPIC = 'vitals'


class VitalsProducer:
    """
    Kafka producer that generates and publishes patient vital signs.
    
    Generates time-series data for multiple simulated patients,
    classifies each reading, and publishes to Kafka.
    """
    
    def __init__(self, kafka_config: Optional[dict] = None):
        """
        Initialize the vitals producer.
        
        Args:
            kafka_config: Optional Kafka producer configuration.
        """
        self.config = kafka_config or KAFKA_CONFIG
        self.producer = Producer(self.config)
        self.classifier = get_classifier()
        
        # Simulated patient IDs
        self.patient_ids = [f"patient-{uuid.uuid4().hex[:8]}" for _ in range(5)]
        
        # Patient baseline vitals (for realistic time-series)
        self.patient_baselines = {
            pid: {
                'heart_rate': random.uniform(65, 85),
                'spo2': random.uniform(96, 99),
                'temperature': random.uniform(36.3, 37.0)
            }
            for pid in self.patient_ids
        }
    
    def _delivery_callback(self, err, msg):
        """Callback for message delivery confirmation."""
        if err:
            print(f"❌ Message delivery failed: {err}")
        else:
            print(f"✓ Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")
    
    def generate_vitals(self, patient_id: str, inject_anomaly: bool = False) -> dict:
        """
        Generate vital signs for a patient.
        
        Args:
            patient_id: The patient identifier.
            inject_anomaly: If True, generate anomalous readings.
            
        Returns:
            Dictionary containing vital signs and classification.
        """
        baseline = self.patient_baselines[patient_id]
        
        if inject_anomaly:
            # Generate critical/warning readings
            anomaly_type = random.choice(['critical', 'warning'])
            if anomaly_type == 'critical':
                heart_rate = random.choice([random.uniform(35, 45), random.uniform(145, 160)])
                spo2 = random.uniform(82, 88)
                temperature = random.choice([random.uniform(34, 35.5), random.uniform(39, 40.5)])
            else:  # warning
                heart_rate = random.choice([random.uniform(50, 60), random.uniform(100, 115)])
                spo2 = random.uniform(90, 95)
                temperature = random.choice([random.uniform(35.5, 36.1), random.uniform(37.3, 38.5)])
        else:
            # Normal readings with natural variation
            heart_rate = baseline['heart_rate'] + random.gauss(0, 3)
            spo2 = baseline['spo2'] + random.gauss(0, 0.5)
            temperature = baseline['temperature'] + random.gauss(0, 0.1)
            
            # Clip to realistic ranges
            heart_rate = max(50, min(120, heart_rate))
            spo2 = max(90, min(100, spo2))
            temperature = max(35.5, min(38.5, temperature))
        
        # Create reading and classify
        reading = VitalReading(
            heart_rate=round(heart_rate, 1),
            spo2=round(spo2, 1),
            temperature=round(temperature, 2)
        )
        
        state_classified = self.classifier.classify(reading)
        
        return {
            'patient_id': patient_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'vitals': {
                'heart_rate': reading.heart_rate,
                'spo2': reading.spo2,
                'temperature': reading.temperature
            },
            'state_classified': state_classified,
            'device_id': f"edge-{hash(patient_id) % 1000:03d}"
        }
    
    def publish(self, data: dict) -> None:
        """
        Publish vital signs data to Kafka.
        
        Args:
            data: Dictionary containing vital signs payload.
        """
        try:
            self.producer.produce(
                topic=VITALS_TOPIC,
                key=data['patient_id'].encode('utf-8'),
                value=json.dumps(data).encode('utf-8'),
                callback=self._delivery_callback
            )
            self.producer.poll(0)  # Trigger callbacks
        except KafkaError as e:
            print(f"❌ Failed to produce message: {e}")
    
    def run(self, interval_seconds: int = 5, anomaly_probability: float = 0.1):
        """
        Run the producer, generating and publishing vitals continuously.
        
        Args:
            interval_seconds: Seconds between publications.
            anomaly_probability: Probability of generating anomalous readings.
        """
        print(f"🚀 Starting Vitals Producer")
        print(f"   → Kafka: {self.config['bootstrap.servers']}")
        print(f"   → Topic: {VITALS_TOPIC}")
        print(f"   → Patients: {len(self.patient_ids)}")
        print(f"   → Interval: {interval_seconds}s")
        print(f"   → Anomaly Rate: {anomaly_probability * 100}%")
        print("-" * 50)
        
        try:
            while True:
                for patient_id in self.patient_ids:
                    # Randomly inject anomalies
                    inject_anomaly = random.random() < anomaly_probability
                    
                    vitals_data = self.generate_vitals(patient_id, inject_anomaly)
                    
                    # Log the reading
                    state = vitals_data['state_classified']
                    state_emoji = {'Normal': '🟢', 'Warning': '🟡', 'Critical': '🔴'}[state]
                    print(f"{state_emoji} [{vitals_data['timestamp'][:19]}] "
                          f"{patient_id}: HR={vitals_data['vitals']['heart_rate']}, "
                          f"SpO2={vitals_data['vitals']['spo2']}, "
                          f"Temp={vitals_data['vitals']['temperature']} "
                          f"→ {state}")
                    
                    self.publish(vitals_data)
                
                # Flush any pending messages
                self.producer.flush(timeout=1)
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n⏹ Stopping producer...")
        finally:
            self.producer.flush(timeout=10)
            print("✓ Producer stopped cleanly")


def main():
    """Main entry point."""
    producer = VitalsProducer()
    producer.run(interval_seconds=5, anomaly_probability=0.15)


if __name__ == '__main__':
    main()
