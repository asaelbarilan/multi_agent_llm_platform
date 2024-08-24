import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_solve_problem():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/solve", json={"prompt": "how much is 1+1"})

        assert response.status_code == 200
        content = response.text.splitlines()

        assert "Agent1:" in content[0]
        assert "Solution verified, stopping conversation." in content[-1]

if __name__ == '__main__':
    pytest.main()
