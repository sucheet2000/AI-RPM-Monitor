"""
Tests for the Edge Classifier.

Verifies that the classifier correctly identifies Normal, Warning,
and Critical vital readings.
"""
import pytest
import numpy as np
from edge_classifier import EdgeClassifier, VitalReading, get_classifier, VITAL_RANGES


class TestVitalReading:
    """Tests for VitalReading dataclass."""
    
    def test_to_array(self):
        """Test conversion to numpy array."""
        reading = VitalReading(heart_rate=75, spo2=98, temperature=36.6)
        arr = reading.to_array()
        
        assert arr.shape == (1, 3)
        assert arr[0, 0] == 75
        assert arr[0, 1] == 98
        assert arr[0, 2] == 36.6


class TestEdgeClassifier:
    """Tests for EdgeClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create a trained classifier."""
        return get_classifier()
    
    @pytest.fixture
    def untrained_classifier(self):
        """Create an untrained classifier."""
        return EdgeClassifier()
    
    # Normal readings tests
    def test_normal_reading(self, classifier):
        """Test classification of normal vital signs."""
        reading = VitalReading(heart_rate=75, spo2=98, temperature=36.6)
        assert classifier.classify(reading) == 'Normal'
    
    def test_normal_reading_edge_of_range(self, classifier):
        """Test normal classification at edge of normal range."""
        reading = VitalReading(heart_rate=60, spo2=95, temperature=37.2)
        assert classifier.classify(reading) == 'Normal'
    
    # Critical readings tests - Heart Rate
    def test_critical_low_heart_rate(self, classifier):
        """Test critical classification for dangerously low heart rate."""
        reading = VitalReading(heart_rate=35, spo2=98, temperature=36.6)
        assert classifier.classify(reading) == 'Critical'
    
    def test_critical_high_heart_rate(self, classifier):
        """Test critical classification for dangerously high heart rate."""
        reading = VitalReading(heart_rate=160, spo2=98, temperature=36.6)
        assert classifier.classify(reading) == 'Critical'
    
    # Critical readings tests - SpO2
    def test_critical_low_spo2(self, classifier):
        """Test critical classification for dangerously low oxygen saturation."""
        reading = VitalReading(heart_rate=75, spo2=85, temperature=36.6)
        assert classifier.classify(reading) == 'Critical'
    
    def test_critical_spo2_at_threshold(self, classifier):
        """Test critical classification at SpO2 critical threshold."""
        reading = VitalReading(heart_rate=75, spo2=88, temperature=36.6)
        assert classifier.classify(reading) == 'Critical'
    
    # Critical readings tests - Temperature
    def test_critical_low_temperature(self, classifier):
        """Test critical classification for hypothermia."""
        reading = VitalReading(heart_rate=75, spo2=98, temperature=34.5)
        assert classifier.classify(reading) == 'Critical'
    
    def test_critical_high_temperature(self, classifier):
        """Test critical classification for high fever."""
        reading = VitalReading(heart_rate=75, spo2=98, temperature=40.0)
        assert classifier.classify(reading) == 'Critical'
    
    # Warning readings tests
    def test_warning_elevated_heart_rate(self, classifier):
        """Test warning classification for elevated heart rate."""
        reading = VitalReading(heart_rate=110, spo2=98, temperature=36.6)
        assert classifier.classify(reading) == 'Warning'
    
    def test_warning_low_heart_rate(self, classifier):
        """Test warning classification for low heart rate."""
        reading = VitalReading(heart_rate=55, spo2=98, temperature=36.6)
        assert classifier.classify(reading) == 'Warning'
    
    def test_warning_low_spo2(self, classifier):
        """Test warning classification for mildly low oxygen."""
        reading = VitalReading(heart_rate=75, spo2=92, temperature=36.6)
        assert classifier.classify(reading) == 'Warning'
    
    def test_warning_elevated_temperature(self, classifier):
        """Test warning classification for mild fever."""
        reading = VitalReading(heart_rate=75, spo2=98, temperature=38.0)
        assert classifier.classify(reading) == 'Warning'
    
    # Multiple abnormal vitals
    def test_critical_multiple_abnormal(self, classifier):
        """Test critical classification when multiple vitals are abnormal."""
        reading = VitalReading(heart_rate=155, spo2=86, temperature=39.8)
        assert classifier.classify(reading) == 'Critical'
    
    # Batch classification
    def test_classify_batch(self, classifier):
        """Test batch classification of multiple readings."""
        readings = [
            VitalReading(heart_rate=75, spo2=98, temperature=36.6),   # Normal
            VitalReading(heart_rate=110, spo2=93, temperature=37.5),  # Warning
            VitalReading(heart_rate=160, spo2=85, temperature=40.0),  # Critical
        ]
        
        results = classifier.classify_batch(readings)
        
        assert results[0] == 'Normal'
        assert results[1] == 'Warning'
        assert results[2] == 'Critical'
    
    # Training data generation
    def test_generate_training_data_shape(self, untrained_classifier):
        """Test training data generation produces correct shape."""
        data = untrained_classifier.generate_training_data(n_samples=100)
        
        assert data.shape == (100, 3)
    
    def test_generate_training_data_ranges(self, untrained_classifier):
        """Test training data is within realistic ranges."""
        data = untrained_classifier.generate_training_data(n_samples=1000)
        
        # Heart rate
        assert data[:, 0].min() >= 50
        assert data[:, 0].max() <= 120
        
        # SpO2
        assert data[:, 1].min() >= 90
        assert data[:, 1].max() <= 100
        
        # Temperature
        assert data[:, 2].min() >= 35.5
        assert data[:, 2].max() <= 38.5
    
    # Fit method
    def test_fit_sets_is_fitted(self, untrained_classifier):
        """Test that fitting marks classifier as fitted."""
        assert not untrained_classifier.is_fitted
        
        data = untrained_classifier.generate_training_data()
        untrained_classifier.fit(data)
        
        assert untrained_classifier.is_fitted
    
    def test_fit_returns_self(self, untrained_classifier):
        """Test fit returns self for method chaining."""
        data = untrained_classifier.generate_training_data()
        result = untrained_classifier.fit(data)
        
        assert result is untrained_classifier


class TestSyntheticCriticalData:
    """
    Dedicated tests for synthetic Critical data points.
    
    Ensures the classifier correctly identifies all critical conditions.
    """
    
    @pytest.fixture
    def classifier(self):
        return get_classifier()
    
    @pytest.mark.parametrize("heart_rate,spo2,temp,expected", [
        # Critical heart rates
        (30, 98, 36.6, 'Critical'),   # Severe bradycardia
        (40, 98, 36.6, 'Critical'),   # At critical threshold
        (150, 98, 36.6, 'Critical'),  # At critical threshold
        (180, 98, 36.6, 'Critical'),  # Severe tachycardia
        
        # Critical SpO2
        (75, 80, 36.6, 'Critical'),   # Severe hypoxemia
        (75, 85, 36.6, 'Critical'),   # Moderate hypoxemia
        (75, 88, 36.6, 'Critical'),   # At critical threshold
        
        # Critical temperature
        (75, 98, 34.0, 'Critical'),   # Severe hypothermia
        (75, 98, 35.0, 'Critical'),   # At critical low threshold
        (75, 98, 39.5, 'Critical'),   # At critical high threshold
        (75, 98, 41.0, 'Critical'),   # Severe hyperthermia
    ])
    def test_synthetic_critical_data(self, classifier, heart_rate, spo2, temp, expected):
        """Parametrized test for various critical conditions."""
        reading = VitalReading(heart_rate=heart_rate, spo2=spo2, temperature=temp)
        assert classifier.classify(reading) == expected, \
            f"Failed for HR={heart_rate}, SpO2={spo2}, Temp={temp}"
    
    def test_all_critical_combinations(self, classifier):
        """Test that combining multiple critical values still returns Critical."""
        critical_readings = [
            VitalReading(heart_rate=35, spo2=82, temperature=34.0),
            VitalReading(heart_rate=165, spo2=75, temperature=41.5),
            VitalReading(heart_rate=25, spo2=70, temperature=42.0),
        ]
        
        for reading in critical_readings:
            result = classifier.classify(reading)
            assert result == 'Critical', \
                f"Expected Critical for {reading}, got {result}"
