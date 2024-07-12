import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_create_entry(client):
    response = client.post('/create', json={'long_url': 'https://example.com'})
    data = response.get_json()
    assert response.status_code == 200
    assert 'short_url' in data
    assert data['long_url'] == 'https://example.com'

def test_redirect_url(client):
    # Assuming there is a way to set up a known state or mock DB
    client.post('/create', json={'long_url': 'https://example.com', 'custom_url': 'test'})
    response = client.get('/test')
    assert response.status_code == 302
    assert response.location == 'https://example.com'

def test_qr_code_generation(client):
    client.post('/create', json={'long_url': 'https://example.com', 'custom_url': 'test', 'generate_qr': True})
    response = client.get('/qr/test')
    assert response.status_code == 200
    assert response.mimetype == 'image/png'

def test_get_analytics(client):
    response = client.get('/test/analytics')
    assert response.status_code == 200
