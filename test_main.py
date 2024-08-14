import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_solve_problem():
    response = client.post("/solve", json={"prompt": "Test prompt"})
    assert response.status_code == 200
    assert "conversation" in response.json()
    assert "solution" in response.json()

if __name__ == '__main__':
    unittest.main()
