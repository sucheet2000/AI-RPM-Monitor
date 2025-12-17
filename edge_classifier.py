"""
Edge Classifier for Patient Vitals Anomaly Detection.

Uses scikit-learn's Isolation Forest for anomaly detection on vital signs.
Classifies patient data as Normal, Warning, or Critical based on deviation
from normal ranges.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from dataclasses import dataclass
from typing import Literal


# Normal vital sign ranges
VITAL_RANGES = {
    'heart_rate': {'min': 60, 'max': 100, 'critical_low': 40, 'critical_high': 150},
    'spo2': {'min': 95, 'max': 100, 'critical_low': 88, 'critical_high': 100},
    'temperature': {'min': 36.1, 'max': 37.2, 'critical_low': 35.0, 'critical_high': 39.5}
}

StateType = Literal['Normal', 'Warning', 'Critical']


@dataclass
class VitalReading:
    """Data class for a single vital reading."""
    heart_rate: float
    spo2: float
    temperature: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for model input."""
        return np.array([[self.heart_rate, self.spo2, self.temperature]])


class EdgeClassifier:
    """
    Anomaly detection classifier for patient vitals.
    
    Uses a combination of rule-based thresholds and Isolation Forest
    to classify vital readings as Normal, Warning, or Critical.
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize the classifier.
        
        Args:
            contamination: Expected proportion of outliers in training data.
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_fitted = False
        
    def fit(self, training_data: np.ndarray) -> 'EdgeClassifier':
        """
        Fit the Isolation Forest model on training data.
        
        Args:
            training_data: Array of shape (n_samples, 3) with [HR, SpO2, Temp]
            
        Returns:
            Self for method chaining.
        """
        self.model.fit(training_data)
        self.is_fitted = True
        return self
    
    def generate_training_data(self, n_samples: int = 1000) -> np.ndarray:
        """
        Generate synthetic normal vital signs for training.
        
        Args:
            n_samples: Number of samples to generate.
            
        Returns:
            Array of normal vital readings.
        """
        np.random.seed(42)
        
        # Generate normal vitals with some natural variation
        heart_rate = np.random.normal(75, 10, n_samples)
        spo2 = np.random.normal(97, 1.5, n_samples)
        temperature = np.random.normal(36.6, 0.3, n_samples)
        
        # Clip to realistic ranges
        heart_rate = np.clip(heart_rate, 50, 120)
        spo2 = np.clip(spo2, 90, 100)
        temperature = np.clip(temperature, 35.5, 38.5)
        
        return np.column_stack([heart_rate, spo2, temperature])
    
    def _check_critical_thresholds(self, reading: VitalReading) -> bool:
        """Check if any vital is in critical range."""
        ranges = VITAL_RANGES
        
        if (reading.heart_rate <= ranges['heart_rate']['critical_low'] or 
            reading.heart_rate >= ranges['heart_rate']['critical_high']):
            return True
        
        if reading.spo2 <= ranges['spo2']['critical_low']:
            return True
            
        if (reading.temperature <= ranges['temperature']['critical_low'] or 
            reading.temperature >= ranges['temperature']['critical_high']):
            return True
            
        return False
    
    def _check_warning_thresholds(self, reading: VitalReading) -> bool:
        """Check if any vital is in warning range (outside normal but not critical)."""
        ranges = VITAL_RANGES
        
        hr_warning = not (ranges['heart_rate']['min'] <= reading.heart_rate <= ranges['heart_rate']['max'])
        spo2_warning = not (ranges['spo2']['min'] <= reading.spo2 <= ranges['spo2']['max'])
        temp_warning = not (ranges['temperature']['min'] <= reading.temperature <= ranges['temperature']['max'])
        
        return hr_warning or spo2_warning or temp_warning
    
    def classify(self, reading: VitalReading) -> StateType:
        """
        Classify a vital reading as Normal, Warning, or Critical.
        
        Uses rule-based thresholds for Critical detection and combines
        with Isolation Forest anomaly scores for Warning detection.
        
        Args:
            reading: VitalReading object with HR, SpO2, and Temperature.
            
        Returns:
            Classification state: 'Normal', 'Warning', or 'Critical'
        """
        # First check critical thresholds (rule-based)
        if self._check_critical_thresholds(reading):
            return 'Critical'
        
        # Check warning thresholds
        if self._check_warning_thresholds(reading):
            return 'Warning'
        
        # Use Isolation Forest for subtle anomalies
        if self.is_fitted:
            anomaly_score = self.model.decision_function(reading.to_array())[0]
            # Negative scores indicate anomalies
            if anomaly_score < -0.1:
                return 'Warning'
        
        return 'Normal'
    
    def classify_batch(self, readings: list[VitalReading]) -> list[StateType]:
        """Classify multiple readings."""
        return [self.classify(reading) for reading in readings]


# Create a pre-trained classifier instance
def get_classifier() -> EdgeClassifier:
    """Get a pre-trained classifier ready for use."""
    classifier = EdgeClassifier()
    training_data = classifier.generate_training_data()
    classifier.fit(training_data)
    return classifier
