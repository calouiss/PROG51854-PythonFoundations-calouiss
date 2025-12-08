# Unit tests for Library Management System
# Includes tests for Assignment 1–4

import unittest
from fastapi.testclient import TestClient
from app import app, check_compliance, remediate

class TestLibraryAPI(unittest.TestCase):

    def setUp(self):
        # Set up test client before each test
        self.client = TestClient(app)

    # ------------------------
    # Assignment 1 Tests
    # ------------------------
    def test_items_endpoint(self):
        print("\n--- Testing /items endpoint ---")
        response = self.client.get("/items")

        self.assertEqual(response.status_code, 200)
        print(f"Status Code: {response.status_code}")

        data = response.json()
        self.assertIsInstance(data, list)
        print(f"Response is a list with {len(data)} books")

        # Check at least one expected book exists
        self.assertIn("The Spanish Love Deception", data)
        print("Books data is correct")

    def test_health_endpoint(self):
        print("\n--- Testing /health endpoint ---")
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        print(f"Status Code: {response.status_code}")

        data = response.json()
        self.assertEqual(data, {"status": "ok"})
        print(f"Response: {data}")

    # ------------------------
    # Assignment 4 – Compliance Tests
    # ------------------------
    def test_compliance_compliant(self):
        print("\n--- Testing COMPLIANT resource ---")
        resource = {"name": "bucket1", "encrypted": True}

        result = check_compliance(resource)
        self.assertEqual(result, "COMPLIANT")
        print(f"Compliance result: {result}")

    def test_compliance_non_compliant(self):
        print("\n--- Testing NON-COMPLIANT resource ---")
        resource = {"name": "bucket2", "encrypted": False}

        result = check_compliance(resource)
        self.assertEqual(result, "NON_COMPLIANT")
        print(f"Compliance result: {result}")

    # ------------------------
    # Assignment 4 – Remediation Tests
    # ------------------------
    def test_remediation(self):
        print("\n--- Testing remediation function ---")
        resource = {"name": "bucket3", "encrypted": False}

        fixed = remediate(resource)

        # Check encryption was enabled
        self.assertTrue(fixed["encrypted"])
        print(f"Remediated resource: {fixed}")


if __name__ == "__main__":
    print("=" * 50)
    print("Library Management System - Unit Tests (Assignments 1–4)")
    print("=" * 50)
    unittest.main(verbosity=2)
