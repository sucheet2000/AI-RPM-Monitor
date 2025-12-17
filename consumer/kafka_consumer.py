"""
Kafka Consumer with robust error handling and manual offset commits.

Subscribes to the vitals topic and persists messages to PostgreSQL.
Handles common Kafka exceptions gracefully.
Implements At-Least-Once processing via manual offset commits.
"""
import json
import logging
from datetime import datetime
from typing import Optional, Callable
from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VitalsConsumer:
    """
    Kafka Consumer for patient vital signs.
    
    Provides robust error handling for common Kafka issues including:
    - Partition EOF
    - Broker connectivity issues
    - Message decoding errors
    
    Implements At-Least-Once delivery via manual offset commits.
    Offsets are only committed after successful processing.
    """
    
    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9093',
        group_id: str = 'vitals-consumer-group',
        topic: str = 'vitals',
        auto_offset_reset: str = 'earliest'
    ):
        """
        Initialize the Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka broker addresses.
            group_id: Consumer group ID.
            topic: Topic to subscribe to.
            auto_offset_reset: Where to start reading ('earliest' or 'latest').
        """
        self.topic = topic
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': auto_offset_reset,
            # MANUAL COMMIT: Disable auto-commit for At-Least-Once processing
            'enable.auto.commit': False,
            'session.timeout.ms': 30000,
            'max.poll.interval.ms': 300000,
        }
        
        self.consumer: Optional[Consumer] = None
        self.running = False
        
    def connect(self) -> bool:
        """
        Connect to Kafka and subscribe to the topic.
        
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            self.consumer = Consumer(self.config)
            self.consumer.subscribe([self.topic])
            logger.info(f"✓ Connected to Kafka and subscribed to '{self.topic}'")
            logger.info("📍 Manual commit mode enabled (At-Least-Once processing)")
            return True
        except KafkaException as e:
            logger.error(f"✗ Failed to connect to Kafka: {e}")
            return False
    
    def commit_offset(self, msg) -> bool:
        """
        Manually commit the offset for a processed message.
        
        This should only be called after successful processing
        (e.g., after database writes are confirmed).
        
        Args:
            msg: The Kafka message whose offset should be committed.
            
        Returns:
            True if commit successful, False otherwise.
        """
        if not self.consumer:
            logger.error("Cannot commit: consumer not connected")
            return False
            
        try:
            # Commit the offset of the next message (current offset + 1)
            self.consumer.commit(message=msg, asynchronous=False)
            logger.debug(
                f"✓ Committed offset {msg.offset() + 1} "
                f"for partition {msg.partition()}"
            )
            return True
        except KafkaException as e:
            logger.error(f"Failed to commit offset: {e}")
            return False
    
    def _decode_message(self, msg) -> Optional[dict]:
        """
        Decode a Kafka message with error handling.
        
        Args:
            msg: Raw Kafka message.
            
        Returns:
            Decoded message dictionary or None if decoding fails.
        """
        try:
            value = msg.value()
            if value is None:
                logger.warning("Received message with null value")
                return None
            
            return json.loads(value.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e} - Raw value: {msg.value()[:100]}")
            return None
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected decode error: {e}")
            return None
    
    def _handle_kafka_error(self, error: KafkaError) -> bool:
        """
        Handle Kafka errors with appropriate responses.
        
        Args:
            error: KafkaError from message poll.
            
        Returns:
            True if error is recoverable, False if should stop.
        """
        error_code = error.code()
        
        # Partition EOF - normal condition, not an error
        if error_code == KafkaError._PARTITION_EOF:
            logger.debug(f"Reached end of partition (normal)")
            return True
        
        # All brokers down - critical but may recover
        if error_code == KafkaError._ALL_BROKERS_DOWN:
            logger.error("All Kafka brokers are down - will retry")
            return True
        
        # Transport failure
        if error_code == KafkaError._TRANSPORT:
            logger.error(f"Kafka transport error: {error.str()}")
            return True
        
        # Timed out
        if error_code == KafkaError._TIMED_OUT:
            logger.warning("Kafka operation timed out")
            return True
        
        # Unknown topic or partition
        if error_code == KafkaError.UNKNOWN_TOPIC_OR_PART:
            logger.error(f"Unknown topic or partition: {error.str()}")
            return True
        
        # Fatal errors
        if error.code() == KafkaError._FATAL:
            logger.critical(f"Fatal Kafka error: {error.str()}")
            return False
        
        # Other errors
        logger.error(f"Kafka error [{error_code}]: {error.str()}")
        return True
    
    def consume(
        self,
        message_handler: Callable[[dict, int, int, Callable[[], bool]], bool],
        poll_timeout: float = 1.0
    ) -> None:
        """
        Start consuming messages in a loop with manual offset commits.
        
        Args:
            message_handler: Callback function(message_dict, partition, offset, commit_fn).
                             The handler receives a commit function that should be called
                             after successful processing. Returns True if processing succeeded.
            poll_timeout: Seconds to wait for messages.
        """
        if not self.consumer:
            if not self.connect():
                raise RuntimeError("Failed to connect to Kafka")
        
        self.running = True
        logger.info("🚀 Starting Kafka consumer loop (manual commit mode)...")
        
        messages_consumed = 0
        messages_committed = 0
        errors_encountered = 0
        
        try:
            while self.running:
                msg = self.consumer.poll(timeout=poll_timeout)
                
                if msg is None:
                    continue
                
                if msg.error():
                    errors_encountered += 1
                    if not self._handle_kafka_error(msg.error()):
                        logger.critical("Unrecoverable error - stopping consumer")
                        break
                    continue
                
                # Decode message
                data = self._decode_message(msg)
                if data is None:
                    errors_encountered += 1
                    # Still commit for decode failures to avoid infinite retry
                    self.commit_offset(msg)
                    continue
                
                # Create commit callback for this message
                def create_commit_callback(message):
                    def commit_callback() -> bool:
                        return self.commit_offset(message)
                    return commit_callback
                
                # Call message handler with commit callback
                try:
                    success = message_handler(
                        data, 
                        msg.partition(), 
                        msg.offset(),
                        create_commit_callback(msg)
                    )
                    
                    if success:
                        messages_consumed += 1
                        messages_committed += 1
                    else:
                        # Handler returned False - processing failed, don't commit
                        errors_encountered += 1
                        logger.warning(
                            f"Handler failed for message at partition {msg.partition()}, "
                            f"offset {msg.offset()} - will be reprocessed"
                        )
                    
                    if messages_consumed % 100 == 0 and messages_consumed > 0:
                        logger.info(
                            f"Consumed {messages_consumed} messages, "
                            f"Committed {messages_committed}"
                        )
                        
                except Exception as e:
                    logger.error(f"Handler error: {e}")
                    errors_encountered += 1
                    # Don't commit on exception - message will be reprocessed
                    
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.stop()
            logger.info(
                f"Consumer stopped. Consumed: {messages_consumed}, "
                f"Committed: {messages_committed}, Errors: {errors_encountered}"
            )
    
    def stop(self) -> None:
        """Stop the consumer and close connections."""
        self.running = False
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("✓ Consumer closed cleanly")
            except Exception as e:
                logger.error(f"Error closing consumer: {e}")
