import unittest
import requests
import time

BASE_URL = "http://localhost:5000"
SHORTENER_URL = "http://localhost:5001"
QR_CODE_URL = "http://localhost:5002"
ANALYTICS_URL = "http://localhost:5003"

class TestLinkLoom(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Wait for services to start up
        time.sleep(10)

    def test_url_shortening(self):
        response = requests.post(f"{BASE_URL}/create", json={"long_url": "http://example.com"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("short_url", data)
        self.assertEqual(data["long_url"], "http://example.com")

        # Test redirect
        short_url = data["short_url"]
        redirect_response = requests.get(f"{BASE_URL}/{short_url}", allow_redirects=False)
        self.assertEqual(redirect_response.status_code, 302)
        self.assertEqual(redirect_response.headers["Location"], "http://example.com")

    def test_custom_url_shortening(self):
        response = requests.post(f"{BASE_URL}/create", json={"long_url": "http://example.com", "custom_url": "custom123"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["short_url"], "custom123")
        self.assertEqual(data["long_url"], "http://example.com")

    def test_qr_code_generation(self):
        response = requests.post(f"{BASE_URL}/create", json={"long_url": "http://example.com", "generate_qr": True})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("short_url", data)

        # Test QR code retrieval
        short_url = data["short_url"]
        qr_response = requests.get(f"{BASE_URL}/qr/{short_url}")
        self.assertEqual(qr_response.status_code, 200)
        self.assertEqual(qr_response.headers["Content-Type"], "image/png")

    def test_analytics_logging(self):
        response = requests.post(f"{BASE_URL}/create", json={"long_url": "http://example.com"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        short_url = data["short_url"]

        # Access the short URL to generate analytics
        requests.get(f"{BASE_URL}/{short_url}")

        # Test analytics retrieval
        analytics_response = requests.get(f"{BASE_URL}/{short_url}/analytics")
        self.assertEqual(analytics_response.status_code, 200)
        analytics_data = analytics_response.json()
        self.assertGreater(len(analytics_data), 0)

if __name__ == "__main__":
    unittest.main()
