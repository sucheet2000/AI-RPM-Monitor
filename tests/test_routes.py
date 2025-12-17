"""
Tests for application routes.
"""


def test_index_route(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'AI-RPM-Monitor'


def test_vitals_route(client):
    """Test the vitals endpoint."""
    response = client.get('/api/vitals')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
