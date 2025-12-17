"""
Tests for application routes.
"""


def test_index_route(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'AI-RPM-Monitor Consumer'


def test_vitals_route_requires_id(client):
    """Test the vitals endpoint requires patient ID."""
    # /api/vitals without ID should be 404 not found
    response = client.get('/api/vitals')
    assert response.status_code == 404

