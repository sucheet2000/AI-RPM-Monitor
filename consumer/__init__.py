"""
Consumer package for AI-RPM-Monitor.
"""
from consumer.models import db, VitalsRecord, LLMSummary
from consumer.kafka_consumer_ORIGINAL import VitalsConsumer

__all__ = ['db', 'VitalsRecord', 'LLMSummary', 'VitalsConsumer']
