import pytest
import json
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_shorten_url(client):
    response = client.post('/shorten', data=json.dumps({'long_url': 'https://example.com'}), content_type='application/json')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'short_url' in data
    assert data['long_url'] == 'https://example.com'
    assert len(data['short_url']) == 6

def test_shorten_url_with_custom(client):
    response = client.post('/shorten', data=json.dumps({'long_url': 'https://example.com', 'custom_url': 'custom123'}), content_type='application/json')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['short_url'] == 'custom123'
    assert data['long_url'] == 'https://example.com'

def test_invalid_request(client):
    response = client.post('/shorten', data=json.dumps({'invalid_key': 'https://example.com'}), content_type='application/json')
    assert response.status_code == 400
