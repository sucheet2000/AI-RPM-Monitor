"""
API Tests for the Consumer Service.

Tests API endpoints using Flask's test_client with mocked database.
"""
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Set test database URL before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from consumer.app import create_app
from consumer.models import db, VitalsRecord, LLMSummary


@pytest.fixture
def app():
    """Create test application with in-memory SQLite."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_vitals(app):
    """Create sample vital records in the database."""
    with app.app_context():
        records = [
            VitalsRecord(
                patient_id='test-patient-001',
                device_id='edge-001',
                heart_rate=75.0,
                spo2=98.0,
                temperature=36.6,
                state_classified='Normal',
                reading_timestamp=datetime.utcnow() - timedelta(hours=1)
            ),
            VitalsRecord(
                patient_id='test-patient-001',
                device_id='edge-001',
                heart_rate=110.0,
                spo2=93.0,
                temperature=37.5,
                state_classified='Warning',
                reading_timestamp=datetime.utcnow() - timedelta(hours=2)
            ),
            VitalsRecord(
                patient_id='test-patient-001',
                device_id='edge-001',
                heart_rate=160.0,
                spo2=85.0,
                temperature=40.0,
                state_classified='Critical',
                reading_timestamp=datetime.utcnow() - timedelta(minutes=30)
            ),
            VitalsRecord(
                patient_id='test-patient-002',
                device_id='edge-002',
                heart_rate=72.0,
                spo2=97.0,
                temperature=36.8,
                state_classified='Normal',
                reading_timestamp=datetime.utcnow() - timedelta(hours=3)
            ),
        ]
        
        for record in records:
            db.session.add(record)
        db.session.commit()
        
        yield records


class TestHealthCheck:
    """Tests for the health check endpoint."""
    
    def test_health_check_returns_200(self, client):
        """Test health check returns 200 OK."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_health_check_response_structure(self, client):
        """Test health check response has correct structure."""
        response = client.get('/')
        data = response.get_json()
        
        assert 'status' in data
        assert 'service' in data
        assert 'version' in data
        assert data['status'] == 'healthy'


class TestGetVitalsEndpoint:
    """Tests for GET /api/vitals/:patient_id."""
    
    def test_get_vitals_returns_200(self, client, sample_vitals):
        """Test vitals endpoint returns 200 for existing patient."""
        response = client.get('/api/vitals/test-patient-001')
        assert response.status_code == 200
    
    def test_get_vitals_returns_empty_for_unknown_patient(self, client, sample_vitals):
        """Test vitals endpoint returns empty array for unknown patient."""
        response = client.get('/api/vitals/unknown-patient')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['count'] == 0
        assert data['records'] == []
    
    def test_get_vitals_response_structure(self, client, sample_vitals):
        """Test vitals response has correct structure."""
        response = client.get('/api/vitals/test-patient-001')
        data = response.get_json()
        
        assert 'patient_id' in data
        assert 'period_hours' in data
        assert 'count' in data
        assert 'records' in data
        assert isinstance(data['records'], list)
    
    def test_get_vitals_record_structure(self, client, sample_vitals):
        """Test individual vital record has correct structure."""
        response = client.get('/api/vitals/test-patient-001')
        data = response.get_json()
        
        assert data['count'] > 0
        record = data['records'][0]
        
        assert 'id' in record
        assert 'patient_id' in record
        assert 'vitals' in record
        assert 'state_classified' in record
        assert 'reading_timestamp' in record
        
        # Check vitals sub-structure
        vitals = record['vitals']
        assert 'heart_rate' in vitals
        assert 'spo2' in vitals
        assert 'temperature' in vitals
    
    def test_get_vitals_with_hours_parameter(self, client, sample_vitals):
        """Test vitals endpoint respects hours parameter."""
        response = client.get('/api/vitals/test-patient-001?hours=1')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['period_hours'] == 1
    
    def test_get_vitals_with_limit_parameter(self, client, sample_vitals):
        """Test vitals endpoint respects limit parameter."""
        response = client.get('/api/vitals/test-patient-001?limit=1')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['count'] <= 1


class TestGetAlertsEndpoint:
    """Tests for GET /api/alerts/:patient_id."""
    
    def test_get_alerts_returns_200(self, client, sample_vitals):
        """Test alerts endpoint returns 200."""
        response = client.get('/api/alerts/test-patient-001')
        assert response.status_code == 200
    
    def test_get_alerts_only_returns_critical(self, client, sample_vitals):
        """Test alerts endpoint only returns Critical records."""
        response = client.get('/api/alerts/test-patient-001')
        data = response.get_json()
        
        assert response.status_code == 200
        for alert in data['alerts']:
            assert alert['state_classified'] == 'Critical'
    
    def test_get_alerts_response_structure(self, client, sample_vitals):
        """Test alerts response has correct structure."""
        response = client.get('/api/alerts/test-patient-001')
        data = response.get_json()
        
        assert 'patient_id' in data
        assert 'alert_type' in data
        assert 'count' in data
        assert 'alerts' in data
        assert data['alert_type'] == 'Critical'
    
    def test_get_alerts_empty_for_patient_with_no_criticals(self, client, sample_vitals):
        """Test alerts endpoint returns empty for patient with no critical records."""
        response = client.get('/api/alerts/test-patient-002')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['count'] == 0
        assert data['alerts'] == []
    
    def test_get_alerts_with_invalid_since_parameter(self, client, sample_vitals):
        """Test alerts endpoint returns 400 for invalid since parameter."""
        response = client.get('/api/alerts/test-patient-001?since=invalid-date')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestGetSummariesEndpoint:
    """Tests for GET /api/summaries/:patient_id."""
    
    def test_get_summaries_returns_200(self, client, sample_vitals):
        """Test summaries endpoint returns 200."""
        response = client.get('/api/summaries/test-patient-001')
        assert response.status_code == 200
    
    def test_get_summaries_response_structure(self, client, sample_vitals):
        """Test summaries response has correct structure."""
        response = client.get('/api/summaries/test-patient-001')
        data = response.get_json()
        
        assert 'patient_id' in data
        assert 'count' in data
        assert 'summaries' in data
        assert isinstance(data['summaries'], list)


class TestGetStatsEndpoint:
    """Tests for GET /api/stats."""
    
    def test_get_stats_returns_200(self, client, sample_vitals):
        """Test stats endpoint returns 200."""
        response = client.get('/api/stats')
        assert response.status_code == 200
    
    def test_get_stats_response_structure(self, client, sample_vitals):
        """Test stats response has correct structure."""
        response = client.get('/api/stats')
        data = response.get_json()
        
        assert 'total_records' in data
        assert 'patient_count' in data
        assert 'by_state' in data
        assert 'Critical' in data['by_state']
        assert 'Warning' in data['by_state']
        assert 'Normal' in data['by_state']
    
    def test_get_stats_counts_are_accurate(self, client, sample_vitals):
        """Test stats counts match sample data."""
        response = client.get('/api/stats')
        data = response.get_json()
        
        assert data['total_records'] == 4
        assert data['patient_count'] == 2
        assert data['by_state']['Critical'] == 1
        assert data['by_state']['Warning'] == 1
        assert data['by_state']['Normal'] == 2


class TestMockedDatabaseDependency:
    """Tests demonstrating mocked database dependency."""
    
    def test_vitals_endpoint_with_mocked_query(self, app):
        """Test vitals endpoint with fully mocked database query."""
        mock_record = MagicMock()
        mock_record.to_dict.return_value = {
            'id': 1,
            'patient_id': 'mocked-patient',
            'vitals': {'heart_rate': 80, 'spo2': 99, 'temperature': 36.5},
            'state_classified': 'Normal',
            'reading_timestamp': '2024-01-01T00:00:00Z',
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        with app.test_client() as client:
            with patch.object(VitalsRecord, 'query') as mock_query:
                mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_record]
                
                response = client.get('/api/vitals/mocked-patient')
                data = response.get_json()
                
                assert response.status_code == 200
                assert data['count'] == 1
                assert data['records'][0]['patient_id'] == 'mocked-patient'
    
    def test_alerts_endpoint_with_mocked_query(self, app):
        """Test alerts endpoint with fully mocked database query."""
        mock_record = MagicMock()
        mock_record.to_dict.return_value = {
            'id': 1,
            'patient_id': 'mocked-patient',
            'vitals': {'heart_rate': 160, 'spo2': 85, 'temperature': 40.0},
            'state_classified': 'Critical',
            'reading_timestamp': '2024-01-01T00:00:00Z',
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        with app.test_client() as client:
            with patch.object(VitalsRecord, 'query') as mock_query:
                mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_record]
                
                response = client.get('/api/alerts/mocked-patient')
                data = response.get_json()
                
                assert response.status_code == 200
                assert data['count'] == 1
                assert data['alerts'][0]['state_classified'] == 'Critical'
