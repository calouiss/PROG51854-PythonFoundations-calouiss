# Unit tests for Library Management System
# Similar to Exercise4.py testing style

import unittest
from fastapi.testclient import TestClient
from app import app

class TestLibraryAPI(unittest.TestCase):
    
    def setUp(self):
        # Set up test client before each test
        self.client = TestClient(app)
    
    def test_items_endpoint(self):
        # Test /items endpoint
        print("\n--- Testing /items endpoint ---")
        response = self.client.get("/items")
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        print(f"Status Code: {response.status_code}")
        
        # Check response is a list
        data = response.json()
        self.assertIsInstance(data, list)
        print(f"Response is a list with {len(data)} books")
        
        # Check specific book exists
        self.assertIn("The Spanish Love Deception", data)
        print("Books data is correct")
        
    def test_health_endpoint(self):
        # Test /health endpoint
        print("\n--- Testing /health endpoint ---")
        response = self.client.get("/health")
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        print(f"Status Code: {response.status_code}")
        
        # Check response body
        data = response.json()
        self.assertEqual(data, {"status": "ok"})
        print(f"Response: {data}")
        

if __name__ == "__main__":
    print("="*50)
    print("Library Management System - Unit Tests")
    print("="*50)
    unittest.main(verbosity=2)